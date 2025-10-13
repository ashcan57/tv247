#!/usr/bin/env python3
"""
Kodi Repository Builder
=======================
This script zips all addon folders, then generates `addons.xml` and `addons.xml.md5`
for a valid Kodi repository.

💡 Place this script in the root of your repository folder, e.g.:

repository.myaddons/
├── dropbox.downloader/
│   └── addon.xml
├── another.addon/
│   └── addon.xml
└── build_kodi_repo.py
"""

import os
import zipfile
import hashlib
import re

# Paths
REPO_PATH = os.path.dirname(os.path.abspath(__file__))
ZIPS_PATH = os.path.join(REPO_PATH, "zips")
OUTPUT_XML = os.path.join(REPO_PATH, "addons.xml")
OUTPUT_MD5 = os.path.join(REPO_PATH, "addons.xml.md5")

# Ensure zips folder exists
os.makedirs(ZIPS_PATH, exist_ok=True)


def zip_addon(addon_folder):
    """Create a ZIP for the addon based on its version in addon.xml."""
    addon_xml = os.path.join(addon_folder, "addon.xml")
    if not os.path.exists(addon_xml):
        print(f"⚠️  Skipping {addon_folder}: no addon.xml found.")
        return None

    # Extract addon id and version
    with open(addon_xml, "r", encoding="utf-8") as f:
        content = f.read()

    addon_id_match = re.search(r'id="([^"]+)"', content)
    version_match = re.search(r'version="([^"]+)"', content)

    if not addon_id_match or not version_match:
        print(f"⚠️  Skipping {addon_folder}: could not read id/version.")
        return None

    addon_id = addon_id_match.group(1)
    version = version_match.group(1)

    zip_filename = f"{addon_id}-{version}.zip"
    zip_folder = os.path.join(ZIPS_PATH, addon_id)
    os.makedirs(zip_folder, exist_ok=True)
    zip_path = os.path.join(zip_folder, zip_filename)

    # Create the zip file
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(addon_folder):
            for file in files:
                file_path = os.path.join(root, file)
                # Preserve folder structure relative to addon_folder
                arcname = os.path.relpath(file_path, os.path.dirname(addon_folder))
                zipf.write(file_path, arcname)
    print(f"📦  Created {zip_filename}")
    return addon_id


def generate_addons_xml(addon_ids):
    """Combine all addon.xml files into a single addons.xml."""
    xml_content = u'<?xml version="1.0" encoding="UTF-8"?>\n<addons>\n'
    count = 0

    for addon_id in sorted(addon_ids):
        addon_folder = os.path.join(REPO_PATH, addon_id)
        addon_xml = os.path.join(addon_folder, "addon.xml")
        if os.path.exists(addon_xml):
            with open(addon_xml, "r", encoding="utf-8") as f:
                xml_data = f.read().strip()
                if xml_data.startswith("<?xml"):
                    xml_data = xml_data.split("?>", 1)[1]
                xml_content += xml_data.strip() + "\n\n"
                count += 1

    xml_content += "</addons>\n"

    with open(OUTPUT_XML, "w", encoding="utf-8") as f:
        f.write(xml_content)

    print(f"✅ addons.xml generated with {count} addon(s).")


def generate_md5():
    """Create the addons.xml.md5 checksum file."""
    with open(OUTPUT_XML, "rb") as f:
        md5_hash = hashlib.md5(f.read()).hexdigest()

    with open(OUTPUT_MD5, "w") as f:
        f.write(md5_hash)

    print(f"✅ addons.xml.md5 created: {md5_hash}")


def main():
    print("🔧 Building Kodi repository...\n")

    addon_ids = []

    # Loop through all addon folders
    for folder in os.listdir(REPO_PATH):
        addon_folder = os.path.join(REPO_PATH, folder)
        if os.path.isdir(addon_folder) and folder not in ("zips", ".git"):
            addon_id = zip_addon(addon_folder)
            if addon_id:
                addon_ids.append(addon_id)

    if not addon_ids:
        print("⚠️ No valid addons found.")
        return

    generate_addons_xml(addon_ids)
    generate_md5()

    print("\n🎉 Done! Upload this entire folder (including /zips/) to your GitHub repo.")
    print("👉 Kodi source URL example:")
    print("   https://raw.githubusercontent.com/YOUR_USERNAME/repository.myaddons/main/")


if __name__ == "__main__":
    main()
