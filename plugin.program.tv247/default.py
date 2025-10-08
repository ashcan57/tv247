# 247Wizard - safe download-only version
# This script downloads the build zip to Kodi's profile and notifies the user.
# If you want to enable automatic extraction/overwrite, add extraction logic
# locally and test carefully.
import xbmc, xbmcaddon, xbmcgui
import os, urllib.request, shutil

ADDON_ID = 'plugin.program.tv247'
BUILD_URL = 'https://www.dropbox.com/scl/fi/90rsb9oal9dc3fp3g1l8s/dab19.zip?rlkey=5st59x4bq5xpvljnf0rlflu1z&st=rffj6dfn&dl=1'

def download_build(target_path):
    try:
        dialog = xbmcgui.DialogProgress()
        dialog.create('247Wizard', 'Downloading build...')
        urllib.request.urlretrieve(BUILD_URL, target_path)
        dialog.update(100, 'Download complete')
        dialog.close()
        return True
    except Exception as e:
        try:
            dialog.close()
        except:
            pass
        xbmcgui.Dialog().ok('247Wizard', 'Download failed: %s' % str(e))
        return False

def notify_user(msg):
    xbmcgui.Dialog().ok('247Wizard', msg)

def run():
    profile = xbmc.translatePath('special://profile/')
    target = os.path.join(profile, 'dab19.zip')
    ok = download_build(target)
    if not ok:
        return
    # SAFE behavior: we only notify and leave the zip for the user to install manually.
    notify_user('Build downloaded to: %s\n\nTo install: use a file manager or Kodi zip installer.' % target)

if __name__ == '__main__':
    run()
