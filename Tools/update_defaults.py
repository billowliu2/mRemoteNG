#!/usr/bin/env python3
"""Batch-update default settings (binary-safe: preserves BOM and CRLF)."""
import re

def rep(content: bytes, pattern: bytes, new: bytes, label: str):
    result, n = re.subn(pattern, lambda m: m.group(1) + new + m.group(2), content, count=0)
    if n != 1:
        raise SystemExit(f"ERROR {label}: {n} matches (expected 1)")
    return result

def app_config_setting(content: bytes, name: str, old: str, new: str) -> bytes:
    pat = (r'(<setting name="' + re.escape(name) + r'" serializeAs="String">\r?\n\s*<value>)' + re.escape(old) + r'(</value>)').encode()
    return rep(content, pat, new.encode(), f"App.config/{name}")

def settings_file_setting(content: bytes, name: str, old: str, new: str) -> bytes:
    pat = (r'(<Setting Name="' + re.escape(name) + r'"[^>]*>\r?\n\s*<Value Profile="\(Default\)">)' + re.escape(old) + r'(</Value>)').encode()
    return rep(content, pat, new.encode(), f".settings/{name}")

def designer_default(content: bytes, name: str, old: str, new: str) -> bytes:
    pat = (r'(DefaultSettingValueAttribute\(")' + re.escape(old) + r'("\)\]\r?\n\s*public [a-zA-Z]+ ' + re.escape(name) + r' \{)').encode()
    return rep(content, pat, new.encode(), f".Designer.cs/{name}")

def read(p):
    with open(p, 'rb') as f:
        return f.read()

def write(p, c):
    with open(p, 'wb') as f:
        f.write(c)

# ============ Main settings: 4 RDP + 6 convenience = 10 items ============
MAIN = [
    # RDP convenience (from earlier request)
    ("ConDefaultRedirectClipboard", "False", "True"),
    ("ConDefaultRedirectDiskDrives", "False", "True"),
    ("ConDefaultCacheBitmaps", "False", "True"),
    ("ConDefaultEnableFontSmoothing", "False", "True"),
    # Convenience features
    ("SingleClickOnConnectionOpensIt", "False", "True"),
    ("SingleClickSwitchesToOpenConnection", "False", "True"),
    ("TrackActiveConnectionInConnectionTree", "False", "True"),
    ("UseFilterSearch", "False", "True"),
    ("SetHostnameLikeDisplayName", "False", "True"),
    ("MultiSshToolbarVisible", "False", "True"),
]

cfg = read('mRemoteNG/App.config')
sts = read('mRemoteNG/Properties/Settings.settings')
dsg = read('mRemoteNG/Properties/Settings.Designer.cs')
for name, old, new in MAIN:
    cfg = app_config_setting(cfg, name, old, new)
    sts = settings_file_setting(sts, name, old, new)
    dsg = designer_default(dsg, name, old, new)
write('mRemoteNG/App.config', cfg)
write('mRemoteNG/Properties/Settings.settings', sts)
write('mRemoteNG/Properties/Settings.Designer.cs', dsg)

# ============ Page settings = 4 items ============
PAGES = {
    'mRemoteNG/Properties/OptionsStartupExitPage': [
        ("OpenConsFromLastSession", "False", "True"),
        ("SingleInstance", "False", "True"),
    ],
    'mRemoteNG/Properties/OptionsConnectionsPage': [
        ("AutoSaveEveryMinutes", "0", "5"),
    ],
    'mRemoteNG/Properties/OptionsAppearancePage': [
        ("ShowDescriptionTooltipsInTree", "False", "True"),
    ],
}

for base, items in PAGES.items():
    sts = read(base + '.settings')
    dsg = read(base + '.Designer.cs')
    for name, old, new in items:
        sts = settings_file_setting(sts, name, old, new)
        dsg = designer_default(dsg, name, old, new)
    write(base + '.settings', sts)
    write(base + '.Designer.cs', dsg)

print("All 14 settings updated successfully.")
