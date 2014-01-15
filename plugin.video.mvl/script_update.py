from xbmcswift2 import Plugin, xbmcgui, xbmc, xbmcaddon, xbmcplugin, actions
import time

dialog = xbmcgui.Dialog()

xbmc.executebuiltin( "UpdateAddonRepos()" )

#show dialog message
dialog.ok('Please wait...', 'Press the OK Button to begin the update. Please wait until it finishes.')

#freeze UI by showing a busy dialog
xbmc.executebuiltin( "ActivateWindow(busydialog)" )

#wait for 30 seconds
time.sleep(30)

#make everything normal
xbmc.executebuiltin( "Dialog.Close(busydialog)" )
