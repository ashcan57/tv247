"""Build zips, addons.xml and addons.xml.md5 for the TV247 Kodi repository.

Run from the repo root:  python generate.py
Then commit and push everything with GitKraken.
"""
import glob
import hashlib
import os
import re
import zipfile

ADDONS = ["repository.tv247", "plugin.program.tv247.wizard"]
blocks = []

for addon_id in ADDONS:
    xml = open(os.path.join(addon_id, "addon.xml"), encoding="utf-8").read()
    version = re.search(r'<addon[^>]*\sversion="([^"]+)"', xml).group(1)

    # remove old zips so stale versions don't pile up
    for old in glob.glob(os.path.join(addon_id, addon_id + "-*.zip")):
        os.remove(old)

    zip_name = os.path.join(addon_id, "%s-%s.zip" % (addon_id, version))
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(addon_id):
            for f in sorted(files):
                if f.endswith(".zip") or f.startswith("."):
                    continue
                full = os.path.join(root, f)
                z.write(full, full.replace(os.sep, "/"))

    blocks.append(re.sub(r"<\?xml[^>]*\?>", "", xml).strip())
    print("built", zip_name)

out = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n'
out += "\n".join(blocks) + "\n</addons>\n"
with open("addons.xml", "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
with open("addons.xml.md5", "w") as f:
    f.write(hashlib.md5(out.encode("utf-8")).hexdigest())
print("addons.xml and addons.xml.md5 written")

# convenience copy of the repository zip in the root, for easy sharing with family and friends
import shutil
for old in glob.glob("repository.tv247-*.zip"):
    os.remove(old)
repo_version = re.search(r'<addon[^>]*\sversion="([^"]+)"', open("repository.tv247/addon.xml", encoding="utf-8").read()).group(1)
shutil.copy(os.path.join("repository.tv247", "repository.tv247-%s.zip" % repo_version), ".")
print("copied repository zip to root")

# index.html: makes the repo URL browsable (Kodi file manager source) and gives a download page
links = []
for z in sorted(glob.glob("repository.tv247-*.zip")):
    links.append('<a href="%s"><b>%s</b></a> (install this one)<br>' % (z, z))
for addon_id in ADDONS:
    for z in sorted(glob.glob(os.path.join(addon_id, addon_id + "-*.zip"))):
        path = z.replace(os.sep, "/")
        links.append('<a href="%s">%s</a><br>' % (path, os.path.basename(z)))
links.append('<a href="addons.xml">addons.xml</a><br>')
links.append('<a href="addons.xml.md5">addons.xml.md5</a><br>')
html = ("<!DOCTYPE html>\n<html>\n<head><meta charset=\"utf-8\"><title>TV247 Repository</title></head>\n"
        "<body>\n<h1>TV247 Repository</h1>\n<p>Download <b>repository.tv247</b> and install it in Kodi from zip.</p>\n"
        + "\n".join(links) + "\n</body>\n</html>\n")
with open("index.html", "w", encoding="utf-8", newline="\n") as f:
    f.write(html)
print("index.html written")
