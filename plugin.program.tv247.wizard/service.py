import json
import os
import xbmc
import xbmcvfs

FLAG_FILE = os.path.join(xbmcvfs.translatePath("special://home/"), "userdata", "tv247_apply_skin")


def rpc(method, params):
    return xbmc.executeJSONRPC(json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}))


monitor = xbmc.Monitor()

if os.path.exists(FLAG_FILE):
    try:
        with open(FLAG_FILE, "r") as f:
            skin = f.read().strip()
        os.remove(FLAG_FILE)  # remove first so a failure can never loop on every startup
    except Exception:
        skin = ""

    if skin and skin != xbmc.getSkinDir():
        monitor.waitForAbort(8)  # let Kodi finish loading
        xbmc.executebuiltin("UpdateLocalAddons")
        monitor.waitForAbort(2)
        rpc("Addons.SetAddonEnabled", {"addonid": skin, "enabled": True})
        rpc("Settings.SetSettingValue", {"setting": "lookandfeel.skin", "value": skin})
        monitor.waitForAbort(2)
        xbmc.executebuiltin("SendClick(11)")  # accepts the "keep this skin?" prompt
