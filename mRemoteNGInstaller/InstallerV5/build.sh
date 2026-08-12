#!/usr/bin/env bash
# Build the mRemoteNG WiX v5 MSI installer from the actual Release build output.
#
# Prerequisites:
#   - Release build of the main project: mRemoteNG\bin\x64\Release\mRemoteNG.exe
#   - WiX v5 toolset (`dotnet tool install --global wix`)
#   - WiX v5 extensions: WixToolset.UI.wixext
#   - Python 3
set -euo pipefail
cd "$(dirname "$0")"

ROOT="$(cd ../.. && pwd)"
if command -v cygpath >/dev/null 2>&1; then
  ROOT_WIN="$(cygpath -w "$ROOT")"
  BIN_DIR_WIN="$(cygpath -w "$ROOT/mRemoteNG/bin/x64/Release")"
else
  ROOT_WIN="$ROOT"
  BIN_DIR_WIN="$ROOT/mRemoteNG/bin/x64/Release"
fi
BIN_DIR="${BIN_DIR:-$BIN_DIR_WIN}"
CONFIG="${CONFIG:-Release}"
OUT_DIR="bin"

EXE="$BIN_DIR/mRemoteNG.exe"
if [[ ! -f "$EXE" ]]; then
  echo "ERROR: $EXE not found. Build the main project in Release/x64 first." >&2
  exit 1
fi

echo "==> [1/3] Reading version from $EXE"
PRODUCT_VERSION="$(powershell -NoProfile -Command "(Get-Item '$EXE').VersionInfo.FileVersion" | tr -d '\r')"
echo "    ProductVersion = $PRODUCT_VERSION"

echo "==> [2/3] Generating file manifest (Files.wxs)"
python tools/generate_files_wxs.py "$BIN_DIR" "Files.wxs"

echo "==> [3/3] Building MSI"
mkdir -p "$OUT_DIR"
wix build Product.wxs Components.wxs Files.wxs UI/SimpleCustomizeDlg.wxs UI/MyWixUI_FeatureTree.wxs \
  -o "$OUT_DIR/mRemoteNG-Installer.msi" \
  -arch x64 \
  -d "ProductVersion=$PRODUCT_VERSION" \
  -d "SolutionDir=$ROOT_WIN/" \
  -d "Configuration=$CONFIG" \
  -d "BinDir=$BIN_DIR" \
  -ext WixToolset.UI.wixext \
  -culture en-US

echo ""
echo "MSI created: $OUT_DIR/mRemoteNG-Installer.msi"
