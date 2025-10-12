#!/usr/bin/env python3
"""
zip_repo_and_generate_xml.py

- Zips every top‑level addon folder into repo.zip
- Emits addons.xml  (simple <addons><addon>…</addon></addons> list)
- Emits addon.m5d.xml (custom format, you can tweak the template)
"""

import os
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

# ----------------------------------------------------------------------
# Configuration ---------------------------------------------------------
# ----------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.resolve()          # repo base dir
ZIP_NAME = REPO_ROOT / "repo.zip"                    # output zip file
ADDONS_XML = REPO_ROOT / "addons.xml"                # first manifest
M5D_XML = REPO_ROOT / "addon.m5d.xml"                # second manifest

# Define what qualifies as an "addon".  Here we look for a folder that
# contains at least one .py file (you can tighten this rule).
def is_addon(folder: Path) -> bool:
    return any(p.suffix == ".py" for p in folder.iterdir())

# ----------------------------------------------------------------------
# Step 1 – Discover addons -----------------------------------------------
# ----------------------------------------------------------------------
addon_dirs = [p for p in REPO_ROOT.iterdir()
              if p.is_dir() and is_addon(p)]

if not addon_dirs:
    raise RuntimeError("No addon directories found under "
                       f"{REPO_ROOT}")

print(f"Found {len(addon_dirs)} addon(s): {[d.name for d in addon_dirs]}")

# ----------------------------------------------------------------------
# Step 2 – Create the zip ------------------------------------------------
# ----------------------------------------------------------------------
with zipfile.ZipFile(ZIP_NAME, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for addon in addon_dirs:
        for root, _, files in os.walk(addon):
            for file in files:
                full_path = Path(root) / file
                # Archive name should be relative to the repo root
                arc_name = full_path.relative_to(REPO_ROOT)
                zf.write(full_path, arc_name)

print(f"✅ Created zip archive: {ZIP_NAME}")

# ----------------------------------------------------------------------
# Helper – pretty‑print XML (Python 3.9+ has ET.indent)
# ----------------------------------------------------------------------
def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for child in elem:
            indent(child, level+1)
        if not child.tail or not child.tail.strip():
            child.tail = i
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i

# ----------------------------------------------------------------------
# Step 3 – Generate addons.xml -------------------------------------------
# ----------------------------------------------------------------------
root = ET.Element("addons")
for addon in addon_dirs:
    addon_el = ET.SubElement(root, "addon")
    ET.SubElement(addon_el, "name").text = addon.name
    ET.SubElement(addon_el, "path").text = str(addon.relative_to(REPO_ROOT))
    ET.SubElement(addon_el, "timestamp").text = \
        datetime.utcfromtimestamp(addon.stat().st_mtime).isoformat() + "Z"

indent(root)
ET.ElementTree(root).write(ADDONS_XML, encoding="utf-8", xml_declaration=True)
print(f"🗒️  Generated {ADDONS_XML}")

# ----------------------------------------------------------------------
# Step 4 – Generate addon.m5d.xml (custom format) -----------------------
# ----------------------------------------------------------------------
m5d_root = ET.Element("m5dAddons")
for addon in addon_dirs:
    a = ET.SubElement(m5d_root, "addon")
    a.set("id", addon.name)
    a.set("src", f"{addon.name}/")               # relative folder inside zip
    a.set("size", str(sum(f.stat().st_size for f in addon.rglob("*") if f.is_file())))

indent(m5d_root)
ET.ElementTree(m5d_root).write(M5D_XML,
                               encoding="utf-8",
                               xml_declaration=True)
print(f"🗒️  Generated {M5D_XML}")

# ----------------------------------------------------------------------
# Done ------------------------------------------------------------------
# ----------------------------------------------------------------------
print("\nAll done! 🎉\n"
      f"- ZIP:   {ZIP_NAME}\n"
      f"- XML 1: {ADDONS_XML}\n"
      f"- XML 2: {M5D_XML}")