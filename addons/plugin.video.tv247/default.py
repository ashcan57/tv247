import xbmcgui
import xbmcplugin
import sys

# Get the plugin handle from Kodi
handle = int(sys.argv[1])

# Build a simple item list
li = xbmcgui.ListItem(label="Hello from TV247!")
xbmcplugin.addDirectoryItem(handle=handle, url="", listitem=li, isFolder=False)

# Tell Kodi we’re done
xbmcplugin.endOfDirectory(handle)

