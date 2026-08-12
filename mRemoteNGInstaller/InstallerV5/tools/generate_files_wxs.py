#!/usr/bin/env python3
"""Generate Files.wxs for the WiX v5 installer by scanning the release bin directory.

Each file becomes its own component with a deterministic (uuid5) GUID so that
component GUIDs stay stable across rebuilds (required for clean upgrades).
"""
import os
import re
import sys
import uuid

BIN_DIR = os.path.normpath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "mRemoteNG", "bin", "x64", "Release")
OUT = os.path.normpath(sys.argv[2]) if len(sys.argv) > 2 else os.path.join(
    os.path.dirname(__file__), "..", "Files.wxs")

# Files excluded by the original v3 Harvest_Filter.xslt plus noise
def is_excluded(name: str) -> bool:
    lower = name.lower()
    if lower.endswith((".xml", ".config", ".manifest", ".application", ".pdb")):
        return True
    if "vshost" in lower:
        return True
    if lower in ("mremoteng.exe", "puttyng.exe"):
        return True
    return False

def guid_for(relpath: str) -> str:
    return uuid.uuid5(uuid.NAMESPACE_URL, "mremoteng/v5/" + relpath.replace("\\", "/")).hex.upper()

def sanitize_identifier(prefix: str, value: str) -> str:
    """WiX identifiers: must start with a letter/underscore, contain only A-Za-z0-9_."""
    out = re.sub(r"[^A-Za-z0-9_.]", "_", value)
    if not out or not (out[0].isalpha() or out[0] == "_"):
        out = "_" + out
    return prefix + out

def main():
    files = []
    for root, dirs, fnames in os.walk(BIN_DIR):
        for fn in sorted(fnames):
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, BIN_DIR).replace("\\", "/")
            if is_excluded(rel):
                continue
            files.append(rel)

    subdirs = sorted({os.path.dirname(f) for f in files if os.path.dirname(f)})

    # Build a nested directory tree: dict name -> children
    tree = {}
    for d in subdirs:
        parts = d.split("/")
        node = tree
        for p in parts:
            node = node.setdefault(p, {})

    dir_ids = {"": "INSTALLDIR"}
    def dir_id(path: str) -> str:
        if path in dir_ids:
            return dir_ids[path]
        d = sanitize_identifier("Dir.", path.replace("/", "."))
        dir_ids[path] = d
        return d

    for d in subdirs:
        dir_id(d)

    lines = []
    lines.append('<?xml version="1.0" encoding="utf-8"?>')
    lines.append('<Wix xmlns="http://wixtoolset.org/schemas/v4/wxs">')

    # Directory tree fragment (INSTALLDIR is defined in Product.wxs)
    lines.append('  <Fragment>')
    lines.append('    <DirectoryRef Id="INSTALLDIR">')
    def emit_dir(node, indent, prefix):
        for name, children in sorted(node.items()):
            path = f"{prefix}/{name}" if prefix else name
            did = dir_id(path)
            if children:
                lines.append(f'{indent}<Directory Id="{did}" Name="{name}">')
                emit_dir(children, indent + "  ", path)
                lines.append(f'{indent}</Directory>')
            else:
                lines.append(f'{indent}<Directory Id="{did}" Name="{name}" />')
    emit_dir(tree, "      ", "")
    lines.append('    </DirectoryRef>')
    lines.append('  </Fragment>')

    # Components fragment
    lines.append('  <Fragment>')
    lines.append('    <ComponentGroup Id="CG.AppFiles" Directory="INSTALLDIR">')
    for rel in sorted(files):
        gid = guid_for(rel)
        d = os.path.dirname(rel)
        comp_dir = dir_id(d) if d else "INSTALLDIR"
        fid = sanitize_identifier("F.", rel.replace("/", "."))
        lines.append(f'      <Component Id="C.G{gid}" Directory="{comp_dir}" Guid="{gid}">')
        lines.append(f'        <File Id="{fid}" KeyPath="yes" Source="$(var.BinDir)\\{rel}" />')
        lines.append('      </Component>')
    lines.append('    </ComponentGroup>')
    lines.append('  </Fragment>')

    lines.append('</Wix>')

    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")

    print(f"Generated {OUT}: {len(files)} files, {len(subdirs)} subdirs")

if __name__ == "__main__":
    main()
