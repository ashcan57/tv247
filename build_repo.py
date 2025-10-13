import os
import hashlib
import zipfile
import xml.etree.ElementTree as ET

# ----------------------------
# CONFIGURATION
# ----------------------------
REPO_FOLDER = "repository.tv247"         # path to your repository folder
OUTPUT_ZIP = "repository.tv247-1.0.0.zip"  # output zip filename
ADDON_IDS = ["plugin.program.tv247"]    # list of addons to include
VERSION = "1.0.0"
PROVIDER = "ashcan57"

# ----------------------------
# Helper: Create addons.xml
# ----------------------------
def generate_addons_xml(repo_folder, addon_ids):
    addons = ET.Element("addons")

    # Add repository addon itself
    repo_addon = ET.SubElement(addons, "addon", {
        "id": "repository.tv247",
        "name": "TV247 Repository",
        "version": VERSION,
        "provider-name": PROVIDER
    })
    ext_repo = ET.SubElement(repo_addon, "extension", {"point": "xbmc.addon.repository"})
    dir_tag = ET.SubElement(ext_repo, "dir")
    ET.SubElement(dir_tag, "info").text = f"https://raw.githubusercontent.com/{PROVIDER}/tv247/master/repository.tv247/addons.xml"
    ET.SubElement(dir_tag, "checksum").text = f"https://raw.githubusercontent.com/{PROVIDER}/tv247/master/repository.tv247/addons.xml.md5"
    ET.SubElement(dir_tag, "datadir").text = f"https://raw.githubusercontent.com/{PROVIDER}/tv247/master/"
    ET.SubElement(repo_addon, "extension", {"point": "xbmc.addon.metadata"})
    
    # Add each plugin addon
    for addon_id in addon_ids:
        addon_path = os.path.join("plugin.program.tv247")
        addon_xml_path = os.path.join(addon_path, "addon.xml")
        if not os.path.exists(addon_xml_path):
            print(f"Warning: {addon_xml_path} not found. Skipping.")
            continue

        tree = ET.parse(addon_xml_path)
        root = tree.getroot()
        addons.append(root)

    # Write to file
    addons_xml_path = os.path.join(repo_folder, "addons.xml")
    ET.ElementTree(addons).write(addons_xml_path, encoding="utf-8", xml_declaration=True)
    print(f"Generated {addons_xml_path}")
    return addons_xml_path

# ----------------------------
# Helper: Generate MD5
# ----------------------------
def generate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    md5_path = file_path + ".md5"
    with open(md5_path, "w") as f:
        f.write(hash_md5.hexdigest())
    print(f"Generated {md5_path}")
    return md5_path

# ----------------------------
# Helper: Create zip of folder contents
# ----------------------------
def zip_repo(repo_folder, output_zip):
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(repo_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, repo_folder)
                zipf.write(file_path, arcname)
    print(f"Created repository zip: {output_zip}")

# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    addons_xml_path = generate_addons_xml(REPO_FOLDER, ADDON_IDS)
    generate_md5(addons_xml_path)
    zip_repo(REPO_FOLDER, OUTPUT_ZIP)
