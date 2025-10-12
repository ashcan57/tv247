# repo/plugin.video.ev247/default.py
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib.parse

ADDON = xbmcaddon.Addon()
HANDLE = int(sys.argv[1])          # Kodi passes the handle as the second argument
BASE_URL = sys.argv[0]

def list_root():
    """Show a static list of two example streams."""
    streams = [
        {
            'name': 'Sample Stream 1',
            'url':  'https://example.com/stream1.m3u8',
            'thumb': 'https://example.com/thumb1.jpg'
        },
        {
            'name': 'Sample Stream 2',
            'url':  'https://example.com/stream2.m3u8',
            'thumb': 'https://example.com/thumb2.jpg'
        }
    ]

    for s in streams:
        li = xbmcgui.ListItem(label=s['name'])
        li.setArt({'thumb': s['thumb'], 'icon': s['thumb']})
        li.setInfo('video', {'title': s['name'], 'mediatype': 'video'})
        xbmcplugin.addDirectoryItem(handle=HANDLE,
                                    url=s['url'],
                                    listitem=li,
                                    isFolder=False)

    xbmcplugin.endOfDirectory(HANDLE)

def router(paramstring):
    """Simple router – right now we only have the root list."""
    params = dict(urllib.parse.parse_qsl(paramstring))
    if not params:
        list_root()
    else:
        # Future extensions could handle categories, search, etc.
        list_root()

if __name__ == '__main__':
    router(sys.argv[2][1:])   # strip leading '?'
