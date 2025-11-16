import xbmc
import xbmcaddon
import xbmcgui
import os
import zipfile
import shutil
import urllib.request

addon = xbmcaddon.Addon()

PROFILE = xbmcaddon.Addon().getAddonInfo('profile')
PROFILE = xbmc.translatePath(PROFILE) if hasattr(xbmc, 'translatePath') else xbmc.translatePath(PROFILE)

HOME = xbmc.translatePath("special://home/")
TEMP = xbmc.translatePath("special://temp/")

ZIP_URL = "https://www.dropbox.com/scl/fi/glc4wagx7mmdvso88jmiu/encore.zip?rlkey=836o6k19xlppx2ab9ek0zvcbt&dl=1"
ZIP_PATH = os.path.join(TEMP, "encore_build.zip")


def download_build():
    dp = xbmcgui.DialogProgress()
    dp.create("TV247 Installer", "Downloading build...")

    def report(count, block, total):
        pct = int(count * block * 100 / total)
        dp.update(pct, f"Downloading... {pct}%")

    try:
        urllib.request.urlretrieve(ZIP_URL, ZIP_PATH, report)
        dp.update(100, "Download complete.")
        xbmc.sleep(800)
        dp.close()
        return True
    except Exception as e:
        xbmcgui.Dialog().ok("Download Failed", str(e))
        return False


def extract_zip():
    dp = xbmcgui.DialogProgress()
    dp.create("TV247 Installer", "Extracting build...")

    extract_folder = os.path.join(TEMP, "encore_extract")
    shutil.rmtree(extract_folder, ignore_errors=True)
    os.makedirs(extract_folder, exist_ok=True)

    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        files = z.namelist()
        total = len(files)

        for i, f in enumerate(files):
            dp.update(int(i / total * 100), f"Extracting: {f}")
            try:
                z.extract(f, extract_folder)
            except:
                pass

    return extract_folder


def copy_to_kodi(src):
    dp = xbmcgui.DialogProgress()
    dp.create("TV247 Installer", "Copying build...")

    all_files = []
    for root, dirs, files in os.walk(src):
        for f in files:
            all_files.append((root, f))

    total = len(all_files)

    for i, (root, name) in enumerate(all_files):
        pct = int(i / total * 100)
        dp.update(pct, f"Copying: {name}")

        rel = os.path.relpath(root, src)
        dest = os.path.join(HOME, rel)
        os.makedirs(dest, exist_ok=True)

        src_file = os.path.join(root, name)
        dst_file = os.path.join(dest, name)

        try:
            shutil.copy2(src_file, dst_file)
        except PermissionError:
            xbmc.log(f"Locked file skipped: {dst_file}", xbmc.LOGWARNING)
            continue

    dp.update(100, "Install complete.")
    xbmc.sleep(800)
    dp.close()


def full_install():
    if not xbmcgui.Dialog().yesno("TV247 Installer",
                                  "Install Encore Build?\nThis will overwrite your setup.",
                                  yeslabel="Install", nolabel="Cancel"):
        return

    if not download_build():
        return

    extracted = extract_zip()
    copy_to_kodi(extracted)

    xbmcgui.Dialog().ok("TV247 Installer", "Build installed!\nKodi will now close.")
    xbmc.executebuiltin("Quit")


def menu():
    d = xbmcgui.Dialog()
    choice = d.select("TV247 Installer", [
        "Full Install (Encore Build)",
        "Exit"
    ])

    if choice == 0:
        full_install()


menu()
