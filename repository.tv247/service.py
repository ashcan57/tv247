import os
import xbmc
import xbmcaddon
import xbmcvfs

WIZARD = "plugin.program.tv247.wizard"

addon = xbmcaddon.Addon()
profile = xbmcvfs.translatePath(addon.getAddonInfo("profile"))
flag = os.path.join(profile, "wizard_offered")
monitor = xbmc.Monitor()

# Only try once, right after the repository is first installed.
if not xbmc.getCondVisibility("System.HasAddon(%s)" % WIZARD) and not os.path.exists(flag):
    if not os.path.exists(profile):
        xbmcvfs.mkdirs(profile)
    with open(flag, "w") as f:
        f.write("1")

    # give Kodi time to download the repository index
    for attempt in range(3):
        if monitor.waitForAbort(20):
            break
        xbmc.executebuiltin("UpdateAddonRepos")
        if monitor.waitForAbort(15):
            break
        xbmc.executebuiltin("InstallAddon(%s)" % WIZARD)
        if monitor.waitForAbort(25):
            break
        if xbmc.getCondVisibility("System.HasAddon(%s)" % WIZARD):
            break
