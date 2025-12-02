# Ashcan57 Wizard 1.0.1 - FULLY WORKING ON ALL DEVICES (including Firestick)
import xbmc, xbmcgui, xbmcaddon, xbmcvfs
from urllib.request import urlopen
import zipfile
import os

ADDON       = xbmcaddon.Addon()
ADDON_NAME  = ADDON.getAddonInfo('name')
KODI_HOME   = xbmcvfs.translatePath('special://home/')
TEMP_ZIP    = xbmcvfs.translatePath('special://temp/encore_build.zip')
TEMP_EXTRACT= xbmcvfs.translatePath('special://temp/encore_build/')
DROPBOX_URL = "https://www.dropbox.com/scl/fi/glc4wagx7mmdvso88jmiu/encore.zip?rlkey=836o6k19xlppx2ab9ek0zvcbt&dl=1"

def fresh_install():
    if not xbmcgui.Dialog().yesno(ADDON_NAME, "Fresh install Encore build?[CR][CR]This will wipe everything!"):
        return

    progress = xbmcgui.DialogProgress()
    progress.create(ADDON_NAME, "Starting...")

    try:
        # 0-30% Download
        progress.update(0, "Downloading build...")
        resp = urlopen(DROPBOX_URL)
        total = int(resp.headers.get('content-length', 0)) or 1
        down = 0
        chunk = 1024*1024
        with open(TEMP_ZIP, 'wb') as f:
            while True:
                if progress.iscanceled(): raise Exception("Cancelled")
                data = resp.read(chunk)
                if not data: break
                down += len(data)
                f.write(data)
                pc = int(down * 30 / total)
                progress.update(pc, f"Downloading... {down//(1024*1024)} MB")

        # 30-60% Extract
        progress.update(30, "Extracting...")
        with zipfile.ZipFile(TEMP_ZIP, 'r') as z:
            files = z.namelist()
            for i, f in enumerate(files):
                if progress.iscanceled(): raise Exception("Cancelled")
                z.extract(f, TEMP_EXTRACT)
                pc = 30 + int((i+1) * 30 / len(files))
                progress.update(pc, f"Extracting... {i+1}/{len(files)}")

        # 60-90% Android-safe install using xbmcvfs
        progress.update(60, "Installing (Firestick/Android safe)...")
        def copy_tree(src, dst):
            if not xbmcvfs.exists(dst):
                xbmcvfs.mkdirs(dst)
            dirs, files = xbmcvfs.listdir(src)
            for f in files:
                xbmcvfs.copy(src + f, dst + f)
            for d in dirs:
                copy_tree(src + d + '/', dst + d + '/')

        for folder in ['userdata', 'addons']:
            src = TEMP_EXTRACT + folder + '/'
            dst = KODI_HOME + folder + '/'
            if xbmcvfs.exists(src):
                # Clear destination safely
                if xbmcvfs.exists(dst):
                    dirs, files = xbmcvfs.listdir(dst)
                    for f in files: xbmcvfs.delete(dst + f)
                    for d in reversed(dirs): xbmcvfs.rmdir(dst + d, force=True)
                copy_tree(src, dst)

        # 90-100% Cleanup
        progress.update(90, "Cleaning up...")
        if xbmcvfs.exists(TEMP_ZIP): os.remove(TEMP_ZIP)
        if xbmcvfs.exists(TEMP_EXTRACT): 
            dirs, files = xbmcvfs.listdir(TEMP_EXTRACT)
            for f in files: xbmcvfs.delete(TEMP_EXTRACT + f)
            for d in reversed(dirs): xbmcvfs.rmdir(TEMP_EXTRACT + d, force=True)
            xbmcvfs.rmdir(TEMP_EXTRACT)

        progress.update(100, "Complete!")
        progress.close()
        xbmcgui.Dialog().ok(ADDON_NAME, "Encore installed! Restarting...")
        xbmc.executebuiltin('RestartApp')

    except Exception as e:
        progress.close()
        xbmcgui.Dialog().ok("Error", str(e))

# Maintenance tools
def clear_cache():
    path = xbmcvfs.translatePath('special://home/userdata/cache/')
    if xbmcvfs.exists(path):
        dirs, files = xbmcvfs.listdir(path)
        for f in files: xbmcvfs.delete(path + f)
        for d in dirs: xbmcvfs.rmdir(path + d, force=True)
    xbmcgui.Dialog().ok(ADDON_NAME, "Cache cleared")

def clear_thumbnails():
    path = xbmcvfs.translatePath('special://home/userdata/Thumbnails/')
    if xbmcvfs.exists(path): 
        dirs, files = xbmcvfs.listdir(path)
        for f in files: xbmcvfs.delete(path + f)
        for d in dirs: xbmcvfs.rmdir(path + d, force=True)
    xbmcgui.Dialog().ok(ADDON_NAME, "Thumbnails cleared")

def clear_packages():
    path = xbmcvfs.translatePath('special://home/addons/packages/')
    if xbmcvfs.exists(path):
        dirs, files = xbmcvfs.listdir(path)
        for f in files: xbmcvfs.delete(path + f)
        for d in dirs: xbmcvfs.rmdir(path + d, force=True)
    xbmcgui.Dialog().ok(ADDON_NAME, "Packages cleared")

def force_close(): xbmc.executebuiltin('Quit')

# Main menu
def main_menu():
    items = [
        ("Fresh Install Encore", fresh_install),
        ("Clear Cache", clear_cache),
        ("Clear Thumbnails", clear_thumbnails),
        ("Clear Packages", clear_packages),
        ("Force Close Kodi", force_close),
    ]
    while True:
        choice = xbmcgui.Dialog().select("Ashcan57 Wizard", [n for n,_ in items])
        if choice < 0: break
        items[choice][1]()

if __name__ == '__main__':
    main_menu()