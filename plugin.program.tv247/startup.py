import xbmcvfs
import os
import shutil

temp_userdata = xbmcvfs.translatePath("special://home/temp_build/userdata/")
target_userdata = xbmcvfs.translatePath("special://userdata/")

if xbmcvfs.exists(temp_userdata):
    # copy files recursively
    for root, dirs, files in os.walk(temp_userdata):
        rel_path = os.path.relpath(root, temp_userdata)
        dest_dir = os.path.join(target_userdata, rel_path)
        if not xbmcvfs.exists(dest_dir):
            xbmcvfs.mkdirs(dest_dir)
        for file in files:
            src = os.path.join(root, file)
            dst = os.path.join(dest_dir, file)
            try:
                shutil.copy2(src, dst)
            except Exception as e:
                xbmc.log(f"Failed to copy {src}: {e}", xbmc.LOGWARNING)
