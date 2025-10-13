import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import sys

ADDON = xbmcaddon.Addon()
BASE_URL = "https://raw.githubusercontent.com/ashcan57/tv247/main/repository.tv247/"

def add_repo():
    """Add the TV247 repository to Kodi."""
    xbmc.executebuiltin(
        f'InstallAddon({BASE_URL}addons.xml)'
    )
    xbmc.sleep(2000)  # give Kodi a moment to register the repo
    xbmc.executebuiltin('UpdateLocalAddons')
    xbmc.executebuiltin('UpdateAddonRepos')

def install_wizard():
    """Install the wizard itself (this add‑on)."""
    # Since we are already running inside the wizard, nothing else is required.
    xbmcgui.Dialog().notification('TV247 Wizard', 'Repository added successfully', xbmcgui.NOTIFICATION_INFO, 3000)

def run():
    if not xbmc.getCondVisibility('System.HasAddon(repository.tv247)'):
        add_repo()
    else:
        xbmcgui.Dialog().notification('TV247 Wizard',
                                      'Repository already installed',
                                      xbmcgui.NOTIFICATION_INFO,
                                      3000)

    # Optional: auto‑install a downstream add‑on, e.g., plugin.video.tv247
    # xbmc.executebuiltin('InstallAddon(plugin.video.tv247)')

if __name__ == '__main__':
    run()