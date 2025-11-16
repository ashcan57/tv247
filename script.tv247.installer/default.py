import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import os
import zipfile
import shutil
import urllib.request

addon = xbmcaddon.Addon()

# Correct translatePath for Kodi 19+
HOME = xbmcvfs.translatePath("special://home/")
TEMP = xbmcvfs.translatePath("special://temp/")

ZIP_URL = "https://www.dropbox.com/scl/fi/glc4wagx7mmdvso88jmiu/encore.zip?rlkey=836o6k19xlppx2ab9ek0zvcbt&st=vllfs1si&dl=1"
ZIP_PATH = os.path.join(TEMP, "encore_build.zip")


# -------------------------------------------------------
# DOWNLOAD ZIP WITH PROGRESS BAR
# -------------------------------------------------------
def download_build():
    dp = xbmcgui.DialogProgress()
    dp.create("TV247 Installer", "Downloading build...")

    def hook(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        dp.update(percent, f"Downloading build... {percent}%")

    try:
        urllib.request.urlretrieve(ZIP_URL, ZIP_PATH, hook)
        dp.update(100, "Download complete.")
        xbmc.sleep(800)
        dp.close()
        return True

    except Exception as e:
        xbmcgui.Dialog().ok("TV247 Installer", f"Download failed:\n{e}")
        return False


# -------------------------------------------------------
# EXTRACT ZIP SAFELY
# -------------------------------------------------------
def extract_zip():
    dp = xbmcgui.DialogProgress()
    dp.create("TV247 Installer", "Extracting build...")

    extract_path = os.path.join(TEMP, "encore_extract")

    if os.path.exists(extract_path):
        shutil.rmtree(extract_path, ignore_errors=True)

    os.makedirs(extract_path, exist_ok=True)

    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        items = z.namelist()
        total = len(items)

        for i, item in enumerate(items):
            percent = int((i / total) * 100)
            dp.update(percent, f"Extracting: {item}")

            try:
                z.extract(item, extract_path)
            except:
                pass  # skip locked/unfriendly files

    dp.close()
    return extract_path


# -------------------------------------------------------
# COPY FILES INTO KODI (SKIPS LOCKED DLL)
# -------------------------------------------------------
def copy_to_kodi(src):
    dp = xbmcgui.DialogProgress()
    dp.create("TV247 Installer", "Installing build...")

    all_files = []
    for root, dirs, files in os.walk(src):
        for f in files:
            all_files.append((root, f))

    total = len(all_files)

    for i, (root, f) in enumerate(all_files):
        percent = int((i / total) * 100)
        dp.update(percent, f"Installing: {f}")

        rel = os.path.relpath(root, src)
        dest_folder = os.path.join(HOME, rel)

        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder, exist_ok=True)

        src_file = os.path.join(root, f)
        dst_file = os.path.join(dest_folder, f)

        try:
            shutil.copy2(src_file, dst_file)
        except PermissionError:
            # skip locked files (like joystick DLL)
            xbmc.log(f"Skipping locked: {dst_file}", xbmc.LOGWARNING)
            continue

    dp.update(100, "Install complete.")
    xbmc.sleep(700)
    dp.close()


# -------------------------------------------------------
# FULL INSTALL
# -------------------------------------------------------
def full_install():
    ok = xbmcgui.Dialog().yesno("TV247 Installer",
                                "Install the Encore build?\nThis will overwrite Kodi.",
                                yeslabel="Install", nolabel="Cancel")
    if not ok:
        return

    if not download_build():
        return

    extracted = extract_zip()
    copy_to_kodi(extracted)

    xbmcgui.Dialog().ok("TV247 Installer", "Build installed!\nKodi will now restart.")
    xbmc.executebuiltin("Quit")


# -------------------------------------------------------
# MENU
# -------------------------------------------------------
def menu():
    choice = xbmcgui.Dialog().select(
        "TV247 Build Installer",
        [
            "Full Install (Encore Build)",
            "Exit"
        ]
    )

    if choice == 0:
        full_install()
    else:
        return


menu()
