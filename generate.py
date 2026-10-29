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
                if f.endswith(".zip") or f.startswith(".") or f == "index.html":
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

# index pages: plain one-link-per-line format that Kodi's file browser parses reliably
def write_index(path, title, names):
    lines = ["<!DOCTYPE html>", "<html>", "<head><meta charset=\"utf-8\"><title>%s</title></head>" % title,
             "<body>", "<h1>%s</h1>" % title]
    lines += ['<a href="%s">%s</a>' % (n, n) for n in names]
    lines += ["</body>", "</html>", ""]
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))

root_names = sorted(glob.glob("repository.tv247-*.zip"))
write_index("index.html", "TV247 Repository", root_names)

# subfolders get no index page; Kodi reaches them by direct URL
for addon_id in ADDONS:
    p = os.path.join(addon_id, "index.html")
    if os.path.exists(p):
        os.remove(p)
print("index page written")
