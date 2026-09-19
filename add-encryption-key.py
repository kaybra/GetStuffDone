#!/usr/bin/env python3
"""
One-off fixer: adds ITSAppUsesNonExemptEncryption = false to the iOS
Info.plist, so App Store Connect stops asking the "export compliance"
question on every single TestFlight/App Store upload.

Usage:
    python3 add-encryption-key.py ios/App/App/Info.plist
"""
import plistlib
import sys
import shutil

if len(sys.argv) != 2:
    print("Usage: python3 add-encryption-key.py <path-to-Info.plist>")
    sys.exit(1)

path = sys.argv[1]

with open(path, "rb") as f:
    data = plistlib.load(f)

key = "ITSAppUsesNonExemptEncryption"

if key in data:
    print(f"{key} is already set to {data[key]!r} - nothing to do.")
    sys.exit(0)

# Keep a .bak copy just in case
shutil.copy(path, path + ".bak")

data[key] = False

with open(path, "wb") as f:
    plistlib.dump(data, f)

print(f"Added {key} = false to {path} (backup saved as {path}.bak).")
