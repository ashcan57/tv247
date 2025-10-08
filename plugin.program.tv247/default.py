import xbmc
import xbmcgui
import xbmcvfs
import os
import urllib.request
import zipfile

# Dropbox link
dropbox_url = "https://www.dropbox.com/scl/fi/90rsb9oal9dc3fp3g1l8s/dab19.zip?rlkey=5st59x4bq5xpvljnf0rlflu1z&st=ju2x15xu&dl=1"

# Destination path (Kodi userdata folder)
dest_path = xbmcvfs.translatePath(os.path.join(xbmc.translatePath("special://home"), "downloads", "tv247.zip"))

# Show a dialog
dialog = xbmcgui.Dialog()
dialog.notification("TV247", "Downloading build...", xbmcgui.NOTIFICATION_INFO, 5000)

# Download the file
try:
    urllib.request.urlretrieve(dropbox_url, dest_path)
    dialog.notification("TV247", "Download complete!", xbmcgui.NOTIFICATION_INFO, 5000)
except Exception as e:
    dialog.ok("TV247Encore", f"Download failed: {e}")
    exit()

# Optionally extract the zip to Kodi home directory
try:
    extract_path = xbmc.translatePath("special://home/")
    with zipfile.ZipFile(dest_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    dialog.notification("TV247", "Build installed!", xbmcgui.NOTIFICATION_INFO, 5000)
except Exception as e:
    dialog.ok("TV247", f"Extraction failed: {e}")
