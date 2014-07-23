# -*- coding: utf-8 -*- 

import os
import sys
import xbmc
import xbmcaddon

plugin_id = 'plugin.video.mvl'

class DummyAddon:
  def __init__(self):
    self.state = 1

  def getSetting(self, string):
      if string == 'lang':
        if len(xbmcaddon.Addon(id=plugin_id).getSetting(string)) == 0:
          return 'English'
        else:
          return xbmcaddon.Addon(id=plugin_id).getSetting(string)
      elif string == 'OpenSubtitles':
          return "true"
      elif string == 'timeout':
          return 30
      else:
          return "false"

  def setSetting(self, id, value):
      xbmcaddon.Addon(id=plugin_id).setSetting(id, value)
      pass



__addon__      = DummyAddon()
__author__     = 'Mukto Software Ltd.'
__scriptid__   = 'script_subtitles'#script.xbmc.subtitles
__scriptname__ = 'XBMC Subtitles'
__version__    = '3.9.18'
__language__   = xbmcaddon.Addon(id=plugin_id).getLocalizedString



__cwd__        = os.path.dirname(os.path.realpath(__file__)).decode("utf-8")
__profile__    = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'subtitles').decode("utf-8")
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) ).decode("utf-8")

sys.path.append (__resource__)

import gui
from utilities import Pause

if xbmc.Player().isPlayingVideo():
  pause = Pause()
  ui = gui.GUI( "script-XBMC-Subtitles-main.xml" , __cwd__ , "Default")
  if (not ui.set_allparam() or not ui.Search_Subtitles(False)):
    #if __addon__.getSetting("pause") == "true":
    pause.pause()
    ui.doModal()

    del ui
  pause.restore()
  sys.modules.clear()
else:
  #xbmc.executebuiltin((u'Notification(%s,%s,%s)' %(__scriptname__, __language__(611), "1000")).encode("utf-8"))
  ui = gui.GUI( "script-XBMC-Subtitles-main.xml" , __cwd__ , "Default")
  if (not ui.set_allparam() or not ui.Search_Subtitles(False)):
    ui.doModal()

    del ui
  pass




