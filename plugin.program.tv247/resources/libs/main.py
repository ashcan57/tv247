import xbmc
import xbmcgui
import xbmcaddon

ADDON = xbmcaddon.Addon()
BASE_URL = "https://raw.githubusercontent.com/ashcan57/tv247/main/repository.tv247/"

def add_repo():
    """Tell Kodi to download the repository catalog and refresh."""
    xbmc.executebuiltin(f'InstallAddon({BASE_URL}addons.xml)')
    xbmc.sleep(2000)               # give Kodi a moment to register the repo
    xbmc.executebuiltin('UpdateLocalAddons')
    xbmc.executebuiltin('UpdateAddonRepos')

def run():
    if not xbmc.getCondVisibility('System.HasAddon(repository.tv247)'):
        add_repo()
        xbmcgui.Dialog().notification('TV247 Wizard',
                                      'Repository added successfully',
                                      xbmcgui.NOTIFICATION_INFO,
                                      3000)
    else:
        xbmcgui.Dialog().notification('TV247 Wizard',
                                      'Repository already installed',
                                      xbmcgui.NOTIFICATION_INFO,
                                      3000)

if __name__ == '__main__':
    run()