import os
import xbmc
import xbmcaddon
import xbmcvfs

WIZARD = "plugin.program.tv247.wizard"
MAX_STARTUPS = 5   # give up after this many Kodi launches

addon = xbmcaddon.Addon()
profile = xbmcvfs.translatePath(addon.getAddonInfo("profile"))
counter_file = os.path.join(profile, "wizard_attempts")
monitor = xbmc.Monitor()


def wizard_installed():
    return xbmc.getCondVisibility("System.HasAddon(%s)" % WIZARD)


def read_attempts():
    try:
        with open(counter_file, "r") as f:
            return int(f.read().strip())
    except Exception:
        return 0


def write_attempts(n):
    try:
        if not os.path.exists(profile):
            xbmcvfs.mkdirs(profile)
        with open(counter_file, "w") as f:
            f.write(str(n))
    except Exception:
        pass


if not wizard_installed():
    attempts = read_attempts()
    if attempts < MAX_STARTUPS:
        write_attempts(attempts + 1)
        # keep trying this launch until the wizard shows up, in case the repo index is slow to download
        for _ in range(4):
            if monitor.waitForAbort(20):
                break
            xbmc.executebuiltin("UpdateAddonRepos")
            if monitor.waitForAbort(20):
                break
            xbmc.executebuiltin("InstallAddon(%s)" % WIZARD)
            if monitor.waitForAbort(30):
                break
            if wizard_installed():
                break
