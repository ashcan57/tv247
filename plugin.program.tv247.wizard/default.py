import xbmc
import xbmcgui
import xbmcvfs
import urllib.request
import os
import re
import json
import zipfile

BUILD_URL = "https://www.dropbox.com/scl/fi/g7446e9o8kbwb0sgs8au6/matrix.zip?rlkey=vexlkuwv8rz3wz0gpa47te6s0&st=r5hizwm0&dl=1"
BUILD_NAME = "Matrix"
USERDATA = xbmcvfs.translatePath("special://home/")
TEMP_ZIP = xbmcvfs.translatePath("special://temp/matrix.zip")
FLAG_FILE = os.path.join(USERDATA, "userdata", "tv247_apply_skin")
GUISETTINGS = os.path.join(USERDATA, "userdata", "guisettings.xml")


def get_build_skin():
    """Read the skin ID the build was saved with."""
    try:
        with open(GUISETTINGS, "r", encoding="utf-8") as f:
            m = re.search(r'<setting id="lookandfeel\.skin"[^>]*>([^<]+)</setting>', f.read())
        if m and m.group(1).strip():
            return m.group(1).strip()
    except Exception:
        pass
    return ""


def rpc(method, params):
    return xbmc.executeJSONRPC(json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}))


def apply_skin(skin):
    """Switch skin now, while Kodi is running, so Kodi saves it to guisettings.xml on exit."""
    if not skin or skin == xbmc.getSkinDir():
        return
    xbmc.executebuiltin("UpdateLocalAddons")
    xbmc.sleep(3000)
    rpc("Addons.SetAddonEnabled", {"addonid": skin, "enabled": True})
    xbmc.sleep(1500)
    rpc("Settings.SetSettingValue", {"setting": "lookandfeel.skin", "value": skin})
    # accept the "keep this skin?" confirmation
    for _ in range(20):
        xbmc.sleep(500)
        if xbmc.getCondVisibility("Window.IsActive(yesnodialog)"):
            xbmc.executebuiltin("SendClick(11)")
            break
    xbmc.sleep(1500)


def install_build():
    dialog = xbmcgui.Dialog()
    confirm = dialog.yesno("TV247 Wizard", f"Install the {BUILD_NAME} Build?\n\nThis will overwrite your current Kodi setup.", nolabel="Cancel", yeslabel="Install")
    if not confirm:
        return
    progress = xbmcgui.DialogProgress()
    progress.create("TV247 Wizard", "Starting download...")
    try:
        def report(block_num, block_size, total_size):
            if progress.iscanceled():
                raise Exception("Cancelled")
            if total_size > 0:
                downloaded = block_num * block_size
                percent = min(int(downloaded * 100 / total_size), 99)
                mb_done = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                progress.update(percent, f"Downloading {BUILD_NAME} Build...\n{mb_done:.1f} MB of {mb_total:.1f} MB  ({percent}%)")
        urllib.request.urlretrieve(BUILD_URL, TEMP_ZIP, reporthook=report)
        if progress.iscanceled():
            progress.close()
            return
        progress.update(0, "Preparing to install...")
        xbmc.sleep(300)
        with zipfile.ZipFile(TEMP_ZIP, 'r') as z:
            entries = z.infolist()
            total = len(entries)
            for i, entry in enumerate(entries):
                if progress.iscanceled():
                    raise Exception("Cancelled")
                percent = int((i + 1) * 100 / total)
                name = entry.filename if len(entry.filename) <= 50 else "..." + entry.filename[-47:]
                progress.update(percent, f"Installing {BUILD_NAME} Build...\nFile {i + 1} of {total}  ({percent}%)\n{name}")
                try:
                    z.extract(entry, USERDATA)
                except Exception:
                    pass  # locked files (e.g. open databases) are skipped, not fatal
        if os.path.exists(TEMP_ZIP):
            os.remove(TEMP_ZIP)

        # Tell the startup service which skin to apply on next launch
        skin = get_build_skin()
        if skin:
            with open(FLAG_FILE, "w") as f:
                f.write(skin)

        progress.update(100, "Installation complete!")
        xbmc.sleep(800)
        progress.close()

        # switch to the build's skin now (the startup service is only a backup)
        apply_skin(skin)
        restart = dialog.yesno("TV247 Wizard", f"{BUILD_NAME} Build installed successfully!\n\nRestart Kodi now?", nolabel="Later", yeslabel="Restart Now")
        if restart:
            xbmc.executebuiltin("RestartApp")
    except Exception as e:
        progress.close()
        if os.path.exists(TEMP_ZIP):
            os.remove(TEMP_ZIP)
        if "Cancelled" not in str(e):
            dialog.ok("TV247 Wizard", f"Installation failed:\n{str(e)}")


if __name__ == "__main__":
    install_build()
