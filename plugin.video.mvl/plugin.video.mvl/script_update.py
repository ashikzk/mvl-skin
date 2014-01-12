from xbmcswift2 import Plugin, xbmcgui, xbmc, xbmcaddon, xbmcplugin, actions
import time

dialog = xbmcgui.Dialog()

xbmc.executebuiltin( "UpdateAddonRepos()" )

dialog.ok('Please wait...', 'Update is in progress. Please wait until it finishes.')


xbmc.executebuiltin( "ActivateWindow(busydialog)" )

time.sleep(10)

xbmc.executebuiltin( "Dialog.Close(busydialog)" )
