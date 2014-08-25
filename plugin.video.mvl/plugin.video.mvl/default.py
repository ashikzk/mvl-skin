import sys

if 'do_nothing' in sys.argv[0]:
	#no need to do anything!
	exit()

import os

#writes content to a file
def file_write(file_name, data):
	file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name)
	f = open(file_path, 'w')
	if data is not None:
		f.write(data)
	f.close()

#reads content from a file
def file_read(file_name):
	file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name)
	f = open(file_path, 'r')
	data = f.read()
	f.close()

	return data

#########
# load last path
file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'screen_path.dat')
if os.path.exists(file_path):
	f = open(file_path, 'r')
	last_path = f.read()
	f.close()
else:
	last_path = ''

if last_path == sys.argv[0]:
	#same path requested again. no need to load. exit immediately
	#print "SAME PATH"
	xbmc.executebuiltin( "Dialog.Close(busydialog)" )
	exit()

file_write('screen_path.dat', sys.argv[0])

####

#hide any existing loading and show system busy dialog to freeze the screen.
xbmc.executebuiltin( "Dialog.Close(busydialog)" )
xbmc.executebuiltin( "ActivateWindow(busydialog)" )

#save lockdown state to a file for future reference
file_write('screen_lock.dat', 'true')
####


from xbmcswift2 import Plugin, xbmcgui, xbmc, xbmcaddon, xbmcplugin, actions
import urllib2
import time
import calendar
import simplejson as json
import urllib
import urllib2
import xbmcvfs
import xbmcaddon
import xbmcplugin
from t0mm0.common.addon import Addon
import re
import traceback
import shutil

from metahandler import metahandlers
from metahandler import metacontainers

from operator import itemgetter
from threading import Thread

import resources._common as common
from resources import playbackengine
from resources.trie import trie


#Patch Locale for android devices
def getlocale(*args, **kwargs):
	return (None, None)
import locale
locale.getlocale=getlocale
from datetime import datetime


_MVL = Addon(common.plugin_id, sys.argv)
plugin = Plugin()
pluginhandle = int(sys.argv[1])

usrsettings = xbmcaddon.Addon(id=common.plugin_id)
#page_limit = usrsettings.getSetting('page_limit_xbmc')
# authentication = plugin.get_storage('authentication', TTL=1)
# authentication['logged_in'] = 'false'
#username = usrsettings.getSetting('username_xbmc')
#activation_key = usrsettings.getSetting('activationkey_xbmc')
page_limit = 100
username = ''
activation_key = ''
usrsettings.setSetting(id='mac_address', value=usrsettings.getSetting('mac_address'))

THEME_PATH = os.path.join(_MVL.get_path(), 'art')

# server_url = 'http://staging.redbuffer.net/xbmc'
# server_url = 'http://localhost/xbmc'
server_url = 'http://config.myvideolibrary.com'
PREPARE_ZIP = False

__metaget__ = metahandlers.MetaData(preparezip=PREPARE_ZIP)


# try:
# import StorageServer
# except:
# import storageserverdummy as StorageServer
# #cache = StorageServer.StorageServer("mvl_storage_data", 24) # (Your plugin name, Cache time in hours)
# cache = StorageServer.StorageServer("plugin://"+common.plugin_id+"/", 24)
# cache.delete("%")

try:
	from sqlite3 import dbapi2 as orm

	plugin.log.info('Loading sqlite3 as DB engine')
except:
	from pysqlite2 import dbapi2 as orm

plugin.log.info('pysqlite2 as DB engine')
DB = 'sqlite'
__translated__ = xbmc.translatePath("special://database")
DB_DIR = os.path.join(__translated__, 'myvideolibrary.db')
plugin.log.info('DB_DIR: ' + DB_DIR)
mvl_view_mode = 58
mvl_tvshow_title = ''
isAgree = False


@plugin.route('/')
def index():
	global Main_cat
	global last_path

	file_write('quit_log.dat', None)

	if last_path == '':
		file_write('term_agree.dat', 'false')

	# copy pre-cached db
	src_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources', 'data', 'video_cache.db')
	dest_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'userdata', 'addon_data', 'script.module.metahandler', 'meta_cache', 'video_cache.db')
	if not os.path.exists(dest_path) or (os.path.exists(dest_path) and os.path.getsize(dest_path) < os.path.getsize(src_path)):
		shutil.copyfile(src_path, dest_path)

	#clear Current Section name saved in the skin
	xbmc.executebuiltin('Skin.SetString(CurrentSection,)')

	try:
		#set view mode first so that whatever happens, it doesn't change
		mvl_view_mode = 58
	
		
		file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'userdata', 'advancedsettings.xml')
		found = False
		if os.path.exists(file_path):
			file = open(file_path, 'r')
			for line in file:
				if '<showparentdiritems>false</showparentdiritems>' in line:
				#if '<cachemembuffersize>0</cachemembuffersize>' in line:
					found = True
			file.close()

			#do it to make sure we remove network from already existing boxes
			file = open(file_path, 'r')
			for line in file:
				if '<network>' in line:
					found = False
			file.close()


		file_path_keymap = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'userdata', 'keymaps', 'Keyboard.xml')
		found_keymap = False
		if os.path.exists(file_path_keymap):
			file = open(file_path_keymap, 'r')
			for line in file:
				if "<F2>Skin.ToggleSetting('test')</F2>" in line:
					found_keymap = True
			file.close()

			
		if not found or not found_keymap:
			file = open(file_path, 'w')
			file.write('<advancedsettings>\n')
			#file.write('<services>\n')
			#file.write('<upnpannounce>true</upnpannounce>\n')
			#file.write('<upnprenderer>true</upnprenderer>\n')
			#file.write('<upnpserver>true</upnpserver>\n')
			#file.write('<zeroconf>true</zeroconf>\n')
			#file.write('</services>\n')
			#file.write('<network>\n')
			#file.write('<cachemembuffersize>0</cachemembuffersize>\n')
			#file.write('</network>\n')
			file.write('<filelists>\n')
			file.write('<showparentdiritems>false</showparentdiritems>\n')
			file.write('</filelists>\n')
			file.write('<lookandfeel>\n')
			file.write('<skin>'+common.skin_id+'</skin>\n')
			file.write('</lookandfeel>\n')
			file.write('</advancedsettings>\n')
			file.close()
			
			#now create keymap file
			file = open(file_path_keymap, 'w')
			file.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
			file.write('<keymap>\n')
			file.write('<global>\n')
			file.write('<keyboard>\n')
			file.write("<F2>Skin.ToggleSetting('test')</F2>\n")
			file.write("<F3>Skin.ToggleSetting('test')</F3>\n")
			file.write("<F4>Skin.ToggleSetting('test')</F4>\n")
			file.write("<F5>Skin.ToggleSetting('test')</F5>\n")
			file.write("<F6>Skin.ToggleSetting('test')</F6>\n")
			file.write("<backslash>Skin.ToggleSetting('test')</backslash>\n")
			file.write("<backspace>XBMC.RunScript(special://home\\addons\\"+common.plugin_id+"\\script_backhandler.py)</backspace>\n")
			file.write('</keyboard>\n')
			file.write('</global>\n')
			file.write('</keymap>')
						
			hide_busy_dialog()
			
			showMessage('Restart Required', 'Some settings have been changed. You need to restart MyVideoLibrary for the changes to take effect. MyVideoLibrary will now close.')
			
			xbmc.executebuiltin('RestartApp()')
			
			return None
		else:
		
			#if we have found the settings, then this is not the first run
			#we are good to go

			#Media has been clicked
			#Check for update first before proceeding forward
			#if check_update():
			#	 #new update is available
			#	 #return to Home
			#	 sys_exit()
			#	 run_update()
			#	 return None
			##


			# Create a window instance.
			#global isAgree
			check_condition()
			#creating the database if not exists
			init_database()


			#creating a context menu
			#url used to get main categories from server
			url = server_url + "/api/index.php/api/categories_api/getCategories?parent_id=0&limit={0}&page=1".format(page_limit)
			plugin.log.info(url)
			req = urllib2.Request(url)
			opener = urllib2.build_opener()
			f = opener.open(req)
			#reading content fetched from the url
			content = f.read()

			hide_busy_dialog()

			#converting to json object
			jsonObj = json.loads(content)
			items = []

			if isAgree == True:
				show_notification()

				plugin.log.info("here is dialog")
				#creating items from json object
				for categories in jsonObj:
					items += [{
								  'label': '{0}'.format(categories['title']),
								  'path': plugin.url_for('get_categories', id=categories['id'], page=0),
								  'is_playable': False,
								  'thumbnail': art('{0}.png'.format(categories['title'].lower())),
								  'context_menu': [('','',)],
								  'replace_context_menu': True
							  }]

				# hide_busy_dialog()
				return items

	except IOError:
		# xbmc.executebuiltin('Notification(Unreachable Host,Could not connect to server,5000,/error.png)')
		dialog_msg()
		hide_busy_dialog()
		sys_exit()


def setup_internet_check():
	t = Thread(target=check_internet_connection)
	t.daemon = True
	t.start()

def check_quit_log():
	r = file_read('quit_log.dat')

	if r:
		return True
	else:
		return False


# called by each thread
def check_internet_connection():
	sleep_time = 20

	try:
		while(True):
			print 'Starting outbound call to test internet connection'
			url = 'http://www.google.com'
			response = urllib2.urlopen(url, timeout=1)
			count = sleep_time
			while count:
				count = count - 1
				time.sleep(1)

				if check_quit_log():
					return

	except Exception, e:
		print e
		# showMessage('No Connection', 'No internet connection can be found')
		dialog_msg()
		#now setup another thread to continue checking internet connection
		count = sleep_time
		while count:
			count = count - 1
			time.sleep(1)

			if check_quit_log():
				return

		setup_internet_check()


def show_notification():

	try:
		url = server_url + "/api/index.php/api/notification_api/getNotification"
		plugin.log.info(url)
		req = urllib2.Request(url)
		opener = urllib2.build_opener()
		f = opener.open(req)
		#reading content fetched from the url
		content = f.read()
		#converting to json object
		jsonObj = json.loads(content)

		message = jsonObj['message']

		if message != '':
			showMessage('Notification', message)
			sys_exit()
			return True
	except:
		#do nothing
		message = ''

	return False

def onClick_disAgree():
	# window.close()
	sys_exit()


def onClick_agree():
	global isAgree
	# macAddress = usrsettings.getSetting('mac_address')
	# plugin.log.info("I Agree func calls")
	# url = server_url + "/api/index.php/api/authentication_api/set_flag_status?username={0}&mac={1}".format(username, macAddress)
	# req = urllib2.Request(url)
	# opener = urllib2.build_opener()
	# f = opener.open(req)

	file_write('term_agree.dat', 'true')

	isAgree = True


def showMessage(heading, message):
	dialog = xbmcgui.Dialog()
	dialog.ok(heading, message)


def check_condition():

	# macAddress = usrsettings.getSetting('mac_address')
	# global curr_page
	# curr_page = 1
	# url = server_url + "/api/index.php/api/authentication_api/get_flag_status?username={0}&mac={1}".format(username, macAddress)
	# req = urllib2.Request(url)
	# opener = urllib2.build_opener()
	# f = opener.open(req)
	#reading content fetched from the url
	# content = f.read()
	# content = 'false'
	#converting to json object
	# plugin.log.info(url)
	# plugin.log.info(content)

	content = file_read('term_agree.dat')

	if content == 'false':
		#Show Terms & Condition window
		heading = "Terms & Conditions"
		text = file_read('t&c.info')

		print 'tc-text'
		print text

		#dialog = xbmcgui.Dialog()
		#agree_ret = dialog.yesno(heading, text, yeslabel='Agree', nolabel='Disagree')

		terms_popup = CustomTermsPopup('Custom-DialogTerms&Condition.xml', os.path.dirname(os.path.realpath(__file__)))
		terms_popup.updateTermText(heading, text)
		terms_popup.doModal()

		#make sure either Agree or disagree was clicked
		#if none was clicked, then go back to home
		content = file_read('term_agree.dat')
		if content == 'false':
			onClick_disAgree()

	elif content == 'true':
		global isAgree
		isAgree = True
	else:
		plugin.log.info('Closing')
		#sys_exit()


def art(name):
	plugin.log.info('plugin-name')
	plugin.log.info(name)
	art_img = os.path.join(THEME_PATH, name)
	return art_img


def get_mac_address():
	try:
		local_mac_address = xbmc.getInfoLabel('Network.MacAddress')
		if local_mac_address == 'Busy':
			time.sleep(1)
			get_mac_address()
		else:
			return local_mac_address
	except IOError:
		# xbmc.executebuiltin('Notification(Mac Address Not Available,MVL Could not get the MAC Address,5000,/script.hellow.world.png)')
		showMessage('Error','Mac Address Not Available, MVL Could not get the MAC Address')

	# xbmc.executebuiltin('Notification(MAC_Flag Check1,{0},2000)'.format(cache.get("mac_address_flag")))
	# xbmc.executebuiltin('Notification(MAC_Address Check1,{0},2000)'.format(usrsettings.getSetting('mac_address')))

	# if cache.get("mac_address_flag") == 'None' or cache.get("mac_address_flag") == '':
	# cache.set("mac_address_flag", "false")


if usrsettings.getSetting('mac_address') == 'None' or usrsettings.getSetting('mac_address') == '':
	#xbmc.executebuiltin('Notification(MAC_Address Check2,{0},2000)'.format(usrsettings.getSetting('mac_address')))
	plugin.log.info(get_mac_address())
	usrsettings.setSetting(id='mac_address', value='{0}'.format(get_mac_address()))


def check_internet():
	try:
		response = urllib2.urlopen('http://74.125.228.100', timeout=1)
		return True
	except urllib2.URLError as err:
		pass
	return False

def dialog_msg():

	heading = "SYSTEM BUSY"
	text = "Oops! You were unable to connect to MVL. Please try again."

	#show message is a dialog window
	showMessage(heading, text)


def internet_dialog_msg():

	heading = "INTERNET CONNECTION ISSUE"
	# text = "An error has occured communicating with MyVideoLibrary server. Please check that you are connected to internet through wi-fi"
	text = "Your internet connection has been lost. Please wait a few minutes and try again. If the error persists you may wish to contact your Internet Service Provider."

	#show message is a dialog window
	showMessage(heading, text)

def hide_busy_dialog():
	#hide loadign screen
	xbmc.executebuiltin( "Dialog.Close(busydialog)" )

	#clear file content to release lock
	file_write('screen_lock.dat', None)


def show_root():
	global internet_info
	internet_info.close()
	sys_exit()


@plugin.route('/do_nothing/<view_mode>')
def do_nothing(view_mode):
	global mvl_view_mode

	if view_mode != 0:
		mvl_view_mode = view_mode

	hide_busy_dialog()

	return None


@plugin.route('/categories/<id>/<page>')
def get_categories(id, page):
	#import resources.htmlcleaner
	#import re
	global mvl_view_mode

	# showMessage('he he', str(mvl_view_mode))

	mvl_view_mode = 58
	# hide_busy_dialog()
	# return None

	if check_internet():
		global mvl_tvshow_title

		show_notification()

		#save current view mode in case any error occurs and we need to remain on the same page
		prev_view_mode = mvl_view_mode
		button_category = None

		try:

			parent_id = id
			main_category_check = False
			is_search_category = False
			top_level_parent = 0
			page_limit_cat = 100

			xbmcplugin.setContent(pluginhandle, 'Movies')

			plugin.log.info(id)
			plugin.log.info(page)
			plugin.log.info(page_limit_cat)

			url = server_url + "/api/index.php/api/categories_api/getCategories?parent_id={0}&page={1}&limit={2}".format(id,
																														 page,
																														 page_limit_cat)
			plugin.log.info(url)
			req = urllib2.Request(url)
			opener = urllib2.build_opener()
			f = opener.open(req)
			content = f.read()
			items = []
			image_on_off = ''

			if content:
				jsonObj = json.loads(content)
				totalCats = len(jsonObj)
				plugin.log.info('total categories-->%s' % totalCats)
				# plugin.log.info(jsonObj)
				if jsonObj[0]['top_level_parent'] == jsonObj[0]['parent_id']:
					is_search_category = True
					image_on_off = '_off'

				###########
				#if the items are season episodes, we need ot sort them naturally i.e. use Natural Sort for sorting
				if jsonObj[0]['top_level_parent'] == '3' and jsonObj[0]['parent_id'] not in ('32', '3'):
					is_playable = False
					for categories in jsonObj:
						if 'title' not in categories:
							#for the "next" entry
							categories['title'] = '9999999999999999999999999'

						categories['sort_key'] = categories['title'].strip().split(' ')[0]
						categories['sort_key_len'] = len(categories['title'].strip().split(' ')[0])
						categories['title_len'] = len(categories['title'].strip())

						if categories['id'] != -1 and categories['is_playable'] == 'True':
							is_playable = True

					if jsonObj[0]['title'].split(' ')[0].lower() == 'Season'.lower():
						#if items are seasons, then sort them by title length to get correct ordering
						jsonObj.sort(key=lambda x: (x['title_len'], x['title']))
					elif is_playable:
						#otherwise, sort by the first string of the title which should like this: 1x1, 1x2, 1x10, 1x15.....
						jsonObj.sort(key=lambda x: (x['sort_key_len'], x['sort_key']))


				###########

				item_count = len(jsonObj)
				done_count = 0

				dp = xbmcgui.DialogProgress()
				dp_created = False
				dp_type = 'show'

				#sort categories according to release_date except for <Featured> group and TV shows
				if jsonObj[0]['parent_id'] not in ('372395', '372396') and jsonObj[0]['top_level_parent'] != '3':
					release_date_count = 0
					for categories in jsonObj:
						if 'release_date' not in categories:
							categories['release_date'] = '-1'
						elif categories['release_date'] is not None and len(categories['release_date']) == 10:
							#we seem to have got a proper date string
							#make sure we have a valid date format
							try:
								mydate = datetime.strptime(categories['release_date'], '%Y-%m-%d')
							except TypeError:
								mydate = datetime(*(time.strptime(categories['release_date'], '%Y-%m-%d')[0:6]))
							except Exception,e:
								print e

							#put the release_group title in <Month, Year> format
							categories['release_group'] = '[COLOR FF2261B4]'+calendar.month_name[mydate.month] + ', ' + str(mydate.year)+'[/COLOR]'
							release_date_count = 1

					if release_date_count == 0:
						#release_date_count is still 0, meaning we haven't got any release_date in proper date format
						#let's see if we can find any release_date with only year string
						for categories in jsonObj:
							if 'release_date' not in categories:
								categories['release_date'] = '-1'
							elif categories['release_date'] is not None and len(categories['release_date']) == 4:
								#we seem to have got a year string
								#put the release_group title in <Year> format
								categories['release_group'] = '[COLOR FF2261B4]'+categories['release_date']+'[/COLOR]'
								release_date_count = 1

					if release_date_count == 0:
						for categories in jsonObj:
							if 'release_date' not in categories:
								categories['release_date'] = '-1'
							elif categories['release_date'] is not None and len(categories['release_date']) == 4:
								#make sure we have valid date format
								categories['release_group'] = '[COLOR FF2261B4]'+categories['release_date']+'[/COLOR]'
								release_date_count = 1

					#if release_date_count is still 0, it means no entry has a release date
					#no need to sort then
					#otherwise sort in Desc order by release date
					if release_date_count == 1:
						jsonObj.sort(key=lambda x: x['release_date'], reverse=True)

					# print jsonObj

				last_release_group = ''

				for categories in jsonObj:
					try:	# The last item of Json only contains the one element in array with key as "ID" so causing the issue

						plugin.log.info('{0}'.format(categories['is_playable']))
						if categories['top_level_parent'] == categories['parent_id']:
							main_category_check = True

					except:
						pass

					if is_search_category == True:
						is_search_category = False

						if categories['parent_id'] == '1':
							button_name = 'SearchMovies1'
							button_label = 'Search Movies'
						elif categories['parent_id'] == '3':
							button_name = 'SearchTVShows1'
							button_label = 'Search TV Shows'

						#adding search option
						items += [{
								  'label': button_label,
								  'path': plugin.url_for('search', category=parent_id),
								  'thumbnail': art(button_name.lower()+'.png'),
								  'is_playable': False,
								  'context_menu': [('','',)],
								  'replace_context_menu': True
								  }]

					####
					#add an extra item for the release month + year combo
					if 'release_group' in categories:
						if categories['release_group'] != last_release_group:
							if last_release_group == '':
								#that means this is the first line of list
								items += [{
											  'label': '[COLOR FFC41D67]Estimated Release Date[/COLOR]',
											  'path': plugin.url_for('do_nothing', view_mode=0),
											  'is_playable': False,
											  'context_menu': [('','',)],
											  'replace_context_menu': True
										  }]


							last_release_group = categories['release_group']

							items += [{
										  'label': categories['release_group'],
										  'path': plugin.url_for('do_nothing', view_mode=0),
										  'is_playable': False,
										  'context_menu': [('','',)],
										  'replace_context_menu': True
									  }]

					####

					#categories['id'] is -1 when more categories are present and next page option should be displayed
					if categories['id'] == -1:
						items += [{
									  'label': 'Next >>',
									  'path': plugin.url_for('get_categories', id=parent_id, page=(int(page) + 1)),
									  'is_playable': False,
									  'thumbnail': art('next.png'),
									  'context_menu': [('','',)],
									  'replace_context_menu': True
								  }]
					#categories['is_playable'] is False for all categories and True for all video Items
					elif categories['is_playable'] == 'False':

						if categories['top_level_parent'] == '3' and categories['parent_id'] not in ('32', '3'):  # Parsing the TV Shows Titles & Seasons only
							mvl_meta = ''
							#tmpTitle = categories['title'].encode('utf-8')
							#if tmpTitle == "Season 1":
							#	 tmpSeasons = []
							#	 mvl_view_mode = 50
								# for i in range(totalCats):
								# tmpSeasons.append( i )
								#plugin.log.info('season found')
								#mvl_meta = __metaget__.get_seasons(mvl_tvshow_title, '', tmpSeasons)
							is_season = False
							if 'parent_title' in categories:
								#this must be a TV Show Season list
								mvl_meta = create_meta('tvshow', categories['parent_title'].encode('utf-8'), '', '')
								mvl_tvshow_title = categories['parent_title'].encode('utf-8')
								is_season = True
								#xbmcplugin.setContent(pluginhandle, 'Seasons')

							else:
								mvl_meta = create_meta('tvshow', categories['title'].encode('utf-8'), '', '')
								mvl_tvshow_title = categories['title'].encode('utf-8')

							dp_type = 'show'

							#plugin.log.info('meta data-> %s' % mvl_meta)

							thumbnail_url = ''
							try:
								if mvl_meta['cover_url']:
									thumbnail_url = mvl_meta['cover_url']
							except:
								thumbnail_url = ''

							#print "New Thumb"
							#print thumbnail_url

							fanart_url = ''
							try:
								if mvl_meta['backdrop_url']:
									fanart_url = mvl_meta['backdrop_url']
							except:
								fanart_url = ''

							mvl_plot = ''
							try:
								if mvl_meta['plot']:
									mvl_plot = mvl_meta['plot']
							except:
								mvl_plot = ''

							if is_season:
								info_dic = {
										'title': categories['title'].encode('utf-8'),
										}
							else:
								info_dic = {
										  'title': categories['title'].encode('utf-8'),
										  'rating': mvl_meta['rating'],
										  'plot': mvl_plot,
										  'year': mvl_meta['year'],
										  'premiered': mvl_meta['premiered'],
										  'duration': mvl_meta['duration']
										  }

							items += [{
										  'label': '{0}'.format(categories['title'].encode('utf-8')),
										  'path': plugin.url_for('get_categories', id=categories['id'], page=0),
										  'is_playable': False,
										  'thumbnail': thumbnail_url,
										  'properties': {
											  'fanart_image': fanart_url,
										  },
										  'info': info_dic,
										  'context_menu': [('','',)],
										  'replace_context_menu': True
									  }]

						else:

							button_name = categories['title']
							button_category = categories['parent_id']

							if categories['parent_id'] == '1':
								if categories['title'] == 'New Releases':
									button_name = 'DateReleased1'
									categories['title'] = 'Date Released'
								elif categories['title'] == 'Featured':
									button_name = 'Cinema1'
									categories['title'] = 'Cinema Movies'
								elif categories['title'] == 'Genre':
									button_name = 'MovieGenres2'
									categories['title'] = 'Movies by Genre'
							elif categories['parent_id'] == '3':
								if categories['title'] == 'New Releases':
									button_name = 'DateAired1'
									categories['title'] = 'Recently Aired'
								elif categories['title'] == 'Featured':
									button_name = 'PopularTV1'
									categories['title'] = 'Popular TV Series'
								elif categories['title'] == 'Genre':
									button_name = 'TVByGenres1'
									categories['title'] = 'TV Shows by Genre'

							items += [{
										  'label': '{0}'.format(categories['title'].encode('utf-8')),
										  'path': plugin.url_for('get_categories', id=categories['id'], page=0),
										  'is_playable': False,
										  'thumbnail': art('{0}.png'.format(button_name.lower())),
										  'context_menu': [('','',)],
										  'replace_context_menu': True
									  }]

							# print button_name.lower()


					#inorder for the information to be displayed properly, corresponding labels should be added in skin
					elif categories['is_playable'] == 'True':

						if categories['video_id'] == '0':
							#there is something wrong with this playable item. just ignore
							continue

						if categories['source'] == '1':
							thumbnail_url = categories['image_name']
						else:
							thumbnail_url = server_url + '/wp-content/themes/twentytwelve/images/{0}'.format(categories['video_id'] + categories['image_name'])

						mvl_img = thumbnail_url
						series_name = 'NONE'

						watch_info = {'video_type': 'movie', 'season': 'NONE', 'episode': 'NONE', 'year': '0'}

						if categories['top_level_parent'] == '1':
							mvl_meta = create_meta('movie', categories['title'].encode('utf-8'), categories['release_date'], mvl_img)
							watch_info['year'] = mvl_meta['year']
						elif categories['top_level_parent'] == '3':
							#playable items of TV show are episodes
							mvl_meta = create_meta('episode', categories['title'].encode('utf-8'), categories['release_date'], mvl_img, categories['sub_categories_names'])

							watch_info['video_type'] = 'episode'
							watch_info['season'] = mvl_meta['season']
							watch_info['episode'] = mvl_meta['episode']
							watch_info['year'] = mvl_meta['premiered'][:4]

							if watch_info['year'] == '':
								watch_info['year'] = 0


							if 'series_name' in mvl_meta:
								series_name = mvl_meta['series_name'].strip()
							#set layout to Episode
							xbmcplugin.setContent(pluginhandle, 'Episodes')


						plugin.log.info('>> meta data-> %s' % mvl_meta)
						thumbnail_url = ''

						dp_type = 'movie'

						try:
							if mvl_meta['cover_url']:
								thumbnail_url = mvl_meta['cover_url']
						except:
							thumbnail_url = mvl_img

						# New condition added
						if thumbnail_url == '':
							thumbnail_url = art('image-not-available.png')
						fanart_url = ''
						try:
							if mvl_meta['backdrop_url']:
								fanart_url = mvl_meta['backdrop_url']
						except:
							fanart_url = ''

						mvl_plot = ''
						try:
							if mvl_meta['plot']:
								mvl_plot = mvl_meta['plot']
						except:
							mvl_plot = categories['synopsis'].encode('utf-8')

						watched_state = 'Watched'
						if mvl_meta['playcount'] > 0:
							watched_state = 'Unwatched'

						items += [{
									  'thumbnail': thumbnail_url,
									  'properties': {
										  'fanart_image': fanart_url,
									  },
									  'label': '{0}'.format(categories['title'].encode('utf-8')),
									  'info': {
										  'title': categories['title'].encode('utf-8'),
										  'rating': categories['rating'],
										  'comment': categories['synopsis'].encode('utf-8'),
										  'Director': categories['director'].encode('utf-8'),
										  'Producer': categories['producer'],
										  'Writer': categories['writer'],
										  'plot': mvl_plot,
										  'genre': categories['sub_categories_names'],
										  #'cast': categories['actors'].encode('utf-8'),
										  'year': categories['release_date'],
										  'premiered': categories['release_date'],
										  'duration': mvl_meta['duration'],
										  'playcount': mvl_meta['playcount']
									  },
									  'path': plugin.url_for('get_videos', id=categories['video_id'],
															 thumbnail=thumbnail_url, trailer=get_trailer_url(mvl_meta).encode('utf-8'),
															 parent_id=categories['top_level_parent'], series_name=series_name),
									  'is_playable': False,
									  'context_menu': [(
														   'Mark as {0}'.format(watched_state),
														   'XBMC.RunPlugin(%s)' % plugin.url_for('mark_as_{0}'.format(watched_state.lower()),
																								 video_type=watch_info['video_type'],
																								 title=categories['title'].encode('utf-8'),
																								 imdb_id=mvl_meta['imdb_id'],
																								 year=watch_info['year'],
																								 season=watch_info['season'],
																								 episode=watch_info['episode']
																								 )
													   )],
									  'replace_context_menu': True
								  }]

					if categories['id'] != -1:
						if categories['top_level_parent'] == '1':
							dp_type = 'movie'
						elif categories['top_level_parent'] == '3':
							dp_type = 'show'

					if dp_created == False:
						dp.create("Please wait while "+dp_type+" list is loaded","","")
						dp_created = True

					done_count = done_count + 1
					#dp.update((done_count*100/item_count), str(done_count)+" of "+str(item_count)+" "+dp_type+"s loaded so far.")
					dp.update((done_count*100/item_count), str(done_count*100/item_count)+"%")

					if dp.iscanceled():
						break



				if main_category_check == True:
					#adding A-Z listing option
					if button_category == '1':
						button_name = 'AZMovies1'
						button_label = 'Movies A-Z'
					elif button_category == '3':
						button_name = 'AZTvShows1'
						button_label = 'TV Shows A-Z'

					items += [{
								  'label': button_label,
								  'path': plugin.url_for('azlisting', category=parent_id),
								  'thumbnail': art(button_name.lower()+'.png'),
								  'is_playable': False,
								  'context_menu': [('','',)],
								  'replace_context_menu': True
							  }]
					#Most Popular & Favortite are commented out on Client's request for now
					#adding Most Popular option
					# items += [{
					# 'label': 'Most Popular',
					# 'path': plugin.url_for('mostpopular', page=0, category=parent_id),
					# 'thumbnail' : art('pop.png'),
					# 'is_playable': False,
					# }]
					# #adding Favourites option
					# items += [{
					# 'label': 'Favourites',
					# 'path': plugin.url_for('get_favourites', category=parent_id),
					# 'thumbnail' : art('fav.png'),
					# 'is_playable': False,
					# }]
				#plugin.log.info(items)

				dp.close()

			else:
			   showMessage('No result found', 'Sorry, No information Found Matching Your Query')
			   hide_busy_dialog()
			   exit()				 
			   

			#we should set the view_mode as last thing in this method
			#because if user cancels his action and goes back before the api response
			#the view_mode will still be changed otherwise
			if id in ('23', '32'): # if the Parent ID is Genres for TV or Movies then view should be set as "List" mode
				mvl_view_mode = 50
			elif id in ('1', '3'):	# if these are immediate childs of Top Level parents then view should be set as Fan Art
				mvl_view_mode = 59
			# else:
				# mvl_view_mode = 59

			hide_busy_dialog()

			#plugin.log.info("View mode = " + str(mvl_view_mode))
			#set current section name
			if id == '1':
				xbmc.executebuiltin('Skin.SetString(CurrentSection,Movies)')
			elif id == '3':
				xbmc.executebuiltin('Skin.SetString(CurrentSection,TV)')


			return items
		# except IOError:
			# xbmc.executebuiltin('Notification(Unreachable Host,Could not connect to server,5000,/script.hellow.world.png)')
		except Exception, e:
			print 'Exception...'
			print e

			if id in ('1', '3'):  # if we were on 1st page, then the viewmode should remain to 58 as an error has occured and we haven't got any data for next screen
				mvl_view_mode = 58
			elif id in ('23', '104916', '112504', '32', '104917', '366042', '372395', '372396'):
				mvl_view_mode = 59

			# xbmc.executebuiltin('Notification(Unreachable Host,Could not connect to server,5000,/script.hellow.world.png)')
			dialog_msg()
			hide_busy_dialog()
			# plugin.log.info(e)
			# traceback.print_exc()
	else:
		if id in ('1', '3'):  # if we were on 1st page, then the viewmode should remain to 58 as an error has occured and we haven't got any data for next screen
			mvl_view_mode = 58
		elif id in ('23', '104916', '112504', '32', '104917', '366042', '372395', '372396'):
			mvl_view_mode = 59

		#show internet error message
		internet_dialog_msg()
		hide_busy_dialog()


@plugin.route('/get_videos/<id>/<thumbnail>/<trailer>/<parent_id>/<series_name>')
def get_videos(id, thumbnail, trailer, parent_id, series_name):

	if check_internet():
		show_notification()

		global mvl_view_mode
		mvl_view_mode = 50
		try:
			url = server_url + "/api/index.php/api/categories_api/getVideoUrls?video_id={0}".format(id)
			req = urllib2.Request(url)
			opener = urllib2.build_opener()
			f = opener.open(req)
			content = f.read()
			jsonObj = json.loads(content)

			#plugin.log.info(url)

			url = server_url + "/api/index.php/api/categories_api/getVideoTitle?video_id={0}".format(id)
			req = urllib2.Request(url)
			opener = urllib2.build_opener()
			f = opener.open(req)
			content = f.read()
			items = []
			#plugin.log.info(jsonObj)

			# instruction text
			items += [{
						  #'label': '[COLOR FFFFFF00]Please click on a link below to begin viewing[/COLOR] [COLOR FFFF0000]* HD[/COLOR] [COLOR FFFFFFFF]sources require a minimum of [COLOR FFFF0000]40mb/s[/COLOR] internet speed [COLOR FFFF0000]* Unusable sources[/COLOR] are replaced weekly[/COLOR]',
						  # 'label': '[COLOR FFC41D67]Please click on a link below to begin viewing[/COLOR]',
						  'label': '[COLOR FFC41D67]MVL may have removed certain links to this content based upon DMCA notice[/COLOR]',
						  'path': plugin.url_for('do_nothing', view_mode=mvl_view_mode),
						  'is_playable': False,
						  'context_menu': [('','',)],
						  'replace_context_menu': True
					  }]


			src_list = ['movreel', 'mightyupload', 'promptfile', 'firedrive', 'putlocker', 'novamov', 'nowvideo', 'gorillavid']
			#, 'novamov', 'nowvideo', 'gorillavid']
			#'lemupload',
			#'promptfile', 'mightyupload',
			#'hugefile', 'billionupload', '180upload',
			# 'firedrive', 'putlocker',

			for urls in jsonObj:
				src_order = 0
				for src in src_list:
					if urls['URL'].find(src) >= 0:
						break
					src_order += 1

				urls['src_order'] = src_order

				if urls['resolved_URL'] == '':
					urls['resolved_URL'] = 'NONE'
					if urls['src_order'] > 0:
						urls['src_order'] = len(src_list)+1
					#all un-resolved urls will be marked as <len(src_list)+1>
					#except for the first src <movreel> which will be shown whenever possible
				#elif:
					#put resolved url above all by making it's src_order set to -1
					#urls['src_order'] = len(src_list)

			jsonObj.sort(key=lambda x: x['src_order'])

			count = 0
			sd_count = 0
			for urls in jsonObj:
				# if parent_id == '1' and urls['resolved_URL'] == 'NONE':
				# if un-resolved and not in premium list, then continue
				if urls['resolved_URL'] == 'NONE' and urls['src_order'] == len(src_list)+1:
					continue

				source_quality = ''
				source_url = urls['URL'][urls['URL'].find('://')+3:]
				if source_url.find('www.') != -1:
					source_url = source_url[source_url.find('www.')+4:]

				if not urls['is_hd']:
					source_quality = '*DVD'
					source_color = 'FFFFFFFF'
					sd_count += 1

					if sd_count < 5:
						count += 1

						items += [{
									  'label': '{0} [COLOR FF235B9E]Source {1}[/COLOR] [COLOR {2}]{3}[/COLOR]'.format(content, count, source_color, source_quality),
									  'thumbnail': thumbnail,
									  'path': plugin.url_for('show_popup', url=urls['URL'], resolved_url=urls['resolved_URL'], title='{0}'.format(content), trailer=trailer, parent_id=parent_id, video_id=id, series_name=series_name),
									  'is_playable': False,
									  'context_menu': [('','',)],
									  'replace_context_menu': True
								  }]

			hd_count = 0
			for urls in jsonObj:
				# if urls['resolved_URL'] == 'NONE':
				#	  continue
				if urls['URL'].find('billionupload') >= 0 or urls['URL'].find('180upload') >= 0 or \
						urls['URL'].find('hugefile') >= 0 or urls['URL'].find('megafiles') >= 0 or \
							urls['URL'].find('pandapla') >= 0 or urls['URL'].find('vidhog') >= 0 or \
								urls['URL'].find('epicshare') >= 0 or urls['URL'].find('vidplay') >= 0:
					#discard all these sources for hd
					continue

				source_quality = ''
				source_url = urls['URL'][urls['URL'].find('://')+3:]
				if source_url.find('www.') != -1:
					source_url = source_url[source_url.find('www.')+4:]

				if urls['is_hd']:
					source_quality = '*HD'
					source_color = 'FFC41D67'
					hd_count += 1

					if hd_count < 5:
						count += 1

						items += [{
									  'label': '{0} [COLOR FF235B9E]Source {1}[/COLOR] [COLOR {2}]{3}[/COLOR]'.format(content, count, source_color, source_quality),
									  'thumbnail': thumbnail,
									  'path': plugin.url_for('show_popup', url=urls['URL'], resolved_url=urls['resolved_URL'], title='{0}'.format(content), trailer=trailer, parent_id=parent_id, video_id=id, series_name=series_name),
									  'is_playable': False,
									  'context_menu': [('','',)],
									  'replace_context_menu': True
								  }]


			hide_busy_dialog()
			return items
		except IOError:
			# xbmc.executebuiltin('Notification(Unreachable Host,Could not connect to server,5000,/error.png)')
			dialog_msg()
			hide_busy_dialog()
	else:
		internet_dialog_msg()
		hide_busy_dialog()


video_popup = None

@plugin.route('/show_popup/<url>/<resolved_url>/<title>/<trailer>/<parent_id>/<video_id>/<series_name>')
def show_popup(url, resolved_url, title, trailer, parent_id, video_id, series_name):
	global video_popup

	if parent_id == '1':
		video_popup = CustomPopup('Custom-VideoPopUp-Movies.xml', os.path.dirname(os.path.realpath(__file__)))
	elif parent_id == '3':
		video_popup = CustomPopup('Custom-VideoPopUp-TV.xml', os.path.dirname(os.path.realpath(__file__)))

	series_id = "NONE"
	video_title = title
	if series_name != 'NONE':
		video_title = series_name + ' : ' + title

		mvl_meta = create_meta('tvshow', series_name.encode('utf-8'), '', '')
		series_id = mvl_meta['tvdb_id']

		episode_title = title[title.find(' ')+1:]
		season_text = title[0:title.find(' ')]
		season = season_text[0:season_text.find('x')]
		episode_num = season_text[season_text.find('x')+1:]
		mvl_meta = __metaget__.get_episode_meta(episode_title, mvl_meta['imdb_id'], season, episode_num)

	else:
		mvl_meta = create_meta('movie', title, '', '')
		# series_id = mvl_meta['tmdb_id']


	video_popup.setParams(trailer, url, resolved_url, video_title, video_id, series_id, mvl_meta)
	video_popup.updateLabels()

	try:
		#save current state
		file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'popup_state.dat')
		f = open(file_path, 'w')
		f.write(url+'\n')
		f.write(resolved_url+'\n')
		f.write(title+'\n')
		f.write(trailer+'\n')
		f.write(parent_id+'\n')
		f.write(video_id+'\n')
		f.write(series_name)
		f.close()
	except Exception,e:
		print e

	video_popup.doModal()

	hide_busy_dialog()
	exit()

def show_review(video_id):
	global video_popup

	hide_busy_dialog()
	xbmc.executebuiltin( "ActivateWindow(busydialog)" )

	video_popup = CustomReviewPopup('Custom-ReviewDialog.xml', os.path.dirname(os.path.realpath(__file__)))
	video_popup.setParams('')

	try:
		url = server_url + "/api/index.php/api/review_api/getReview?video_id={0}".format(video_id)
		req = urllib2.Request(url)
		opener = urllib2.build_opener()
		f = opener.open(req)
		#reading content fetched from the url
		content = f.read()
		#converting to json object
		jsonObj = json.loads(content)
		heading = jsonObj['heading']
		review = jsonObj['text']
		critic_name = jsonObj['critic_name']
		review_publish_date = jsonObj['publish_date']

		if len(review) != 0:
			#replace <br> tags with "\n" for better viewing
			review = review.strip("\n")
			review = review.replace("<br>", "\n")
			video_popup.updateReviewText(review, critic_name, review_publish_date, heading)
			video_popup.doModal()
		else:
			showMessage('Sorry!', 'No review found for this movie')
			resume_popup_window()

	except Exception, e:
		pass

	hide_busy_dialog()
	exit()

def resume_popup_window():

	try:
		file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'popup_state.dat')
		f = open(file_path, 'r')
		url = f.readline().strip('\n')

		if len(url) != 0:
			resolved_url = f.readline().strip('\n')
			title = f.readline().strip('\n')
			trailer = f.readline().strip('\n')
			parent_id = f.readline().strip('\n')
			video_id = f.readline().strip('\n')
			series_name = f.readline()
			f.close()

			f = open(file_path, 'w')
			f.close()

			show_popup(url, resolved_url, title, trailer, parent_id, video_id, series_name)
		else:
			f.close()


	except Exception, e:
		pass



def WatchedCallbackwithParams(video_type, title, imdb_id, season, episode, year):
	print('- - -' +'Video completely watched.')

	if video_type == 'movie':
		__metaget__.change_watched(video_type, title, imdb_id, season=None, episode=None, year=year, watched=7)
		# xbmc.executebuiltin("XBMC.Container.Refresh")
	else:
		__metaget__.change_watched(video_type, title, imdb_id, season=season, episode=episode, year=year, watched=7)


def play_video(url, resolved_url, title, video_type, meta):
	global mvl_view_mode

	mvl_view_mode = 50
	#if login is successful then selected item will be resolved using urlresolver and played
	# if login_check():
	unplayable = False
	try:
		# if resolved_url != 'NONE':
		#	  #no need to resolve the url on client side
		#	  #use the pre-resolved url
		#	  hostedurl = resolved_url
		if url.find('youtube.com') != -1:
			#this is youtube video
			#resolve ourselves
			from resources.youtube import YouTubeResolver
			yt = YouTubeResolver()
			host, media_id = yt.get_host_and_id(url)
			hostedurl = yt.get_media_url(host, media_id)
		else:
			#we have to resolve this url on client side cause it isn't pre-resolved or youtube url
			#first import urlresolver
			#as this takes a while, we'll be importing it only when required
			import urlresolver
			print 'Resolving....'
			plugin.log.info(url)
			hostedurl = urlresolver.HostedMediaFile(url).resolve()
			plugin.log.info(hostedurl)

		if str(hostedurl)[0] == 'h':# or str(hostedurl)[0] == 'p':
			source_url = url[ url.find('://')+3: ]
			if source_url.find('www.') != -1:
				source_url = source_url[source_url.find('www.')+4:]

			hide_busy_dialog()
			#plugin.set_resolved_url(hostedurl)

######################
#			 if video_type == 'movie':
#				 mvl_meta = create_meta('movie', title, '', '')
#			 else:
#			 #	   mvl_meta = create_meta('movie', title, '', '')
#				 mvl_meta = {'year': ''}
######################

			playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
			playlist.clear()
			item_title = '[COLOR FFFFFFFF]{0}[/COLOR] | [COLOR FF777777]{1}[/COLOR]'.format(title, source_url)
			listitem = xbmcgui.ListItem(item_title)
			playlist.add(url=hostedurl, listitem=listitem)

			if video_type == 'movie':
				player = playbackengine.Player(addon_id='plugin.video.mvl', video_type='movie', title=title,
										season='', episode='', year=meta['year'], watch_percent=0.9,
										watchedCallbackwithParams=WatchedCallbackwithParams)
			else:
				player = playbackengine.Player(addon_id='plugin.video.mvl', video_type='episode', title=meta['title'],
										season=meta['season'], episode=meta['episode'],
										year='', imdb_id=meta['imdb_id'], watch_percent=0.9,
										watchedCallbackwithParams=WatchedCallbackwithParams)


			player.play(playlist)

			while player._playbackLock.isSet():
				#print('- - -' +'Playback lock set. Sleeping for 250.')
				xbmc.sleep(250)

			#if we are here, it means playback has either stopped or finished
			#show popup again
			resume_popup_window()

			#return None
		else:
			unplayable = True
	except Exception, e:
		unplayable = True
		# print 'EIKHANE ASI'
		print e

	if unplayable:
		#video not playable
		#show error message
		mvl_view_mode = 50
		hide_busy_dialog()
		showMessage('Error loading video', 'This source will not play. Please pick another.')
		return None

	# else: #login_check
	#	  hide_busy_dialog()
	#	  pass

	# else: #check_internet
	#	  mvl_view_mode = 50
	#	  dialog_msg()
	#	  hide_busy_dialog()

def create_meta(video_type, title, year, thumb, sub_cat=None):
	try:
		year = int(year)
	except:
		year = 0
	year = str(year)
	meta = {'title': title, 'year': year, 'imdb_id': '', 'overlay': ''}
	try:
		if video_type == 'tvshow':
			meta = __metaget__.get_meta(video_type, title)
			if not (meta['imdb_id'] or meta['tvdb_id']):
				meta = __metaget__.get_meta(video_type, title, year=year)

		elif video_type == 'movie':	 # movie
			meta = __metaget__.get_meta(video_type, title, year=year)
			alt_id = meta['tmdb_id']

		elif video_type == 'episode': # tv show episode
			series_name = sub_cat[sub_cat.find('_')+1:sub_cat.find('_Season')]
			meta_temp = __metaget__.get_meta('tvshow', series_name)

			episode_title = title[title.find(' ')+1:]
			season_text = title[0:title.find(' ')]
			season = season_text[0:season_text.find('x')]
			episode_num = season_text[season_text.find('x')+1:]
			meta = __metaget__.get_episode_meta(episode_title, meta_temp['imdb_id'], season, episode_num)
			meta['series_name'] = series_name
			#replace episode poster with series poster
			meta['cover_url'] = meta_temp['cover_url']

		#if video_type == 'tvshow':
		#	 meta['cover_url'] = meta['banner_url']
		if meta['cover_url'] in ('/images/noposter.jpg', ''):
			meta['cover_url'] = thumb

		#print 'Done TV'
		#print meta

	except Exception, e:
		print e
		plugin.log.info('Error assigning meta data for %s %s %s' % (video_type, title, year))
		plugin.log.info(e)
		traceback.print_exc()

	return meta

def get_trailer_url(mvl_meta):
	trailer = ''

	if 'trailer_url' in mvl_meta:
		trailer = mvl_meta['trailer_url']

	if trailer == '':
		trailer = 'NONE'

	return trailer

def login_check():
	return True

	try:
		url = server_url + "/api/index.php/api/authentication_api/authenticate_user"
		#urlencode is used to create a json object which will be sent to server in POST
		data = urllib.urlencode({'username': '{0}'.format(username), 'activation_key': '{0}'.format(activation_key),
								 'mac_address_flag': 'false',
								 'mac_address': '{0}'.format(usrsettings.getSetting('mac_address'))})
		req = urllib2.Request(url, data)
		plugin.log.info(url)
		plugin.log.info(data)
		opener = urllib2.build_opener()
		f = opener.open(req)
		#reading content fetched from the url
		content = f.read()

		#converting to json object
		plugin.log.info("Debug_Content: " + content)
		myObj = json.loads(content)
		#plugin.log.info(myObj)

		##creating items from json object
		#for row in myObj:
		#	 if row['status'] == 1:
		#		 return True
		#	 else:
		#		 # xbmc.executebuiltin('Notification(License Limit Reached,' + row['message'] + ')')
		#		 showMessage('Error', 'License Limit Reached for user '+username+', '+ row['message'])
		#		 return False
	except IOError:
		# xbmc.executebuiltin('Notification(Unreachable Host,Could not connect to server,5000,/error.png)')
		dialog_msg()
	pass

from xml.dom import minidom


@plugin.route('/search/<category>/')
def search(category):
	global mvl_view_mode

	if check_internet():
		
		if not show_notification():
		
			try:
				#search_string = plugin.keyboard(heading=('Search Media Engine'))

				#load word list
				if category == '1':
					file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources/data/movie_names.dat')
				else:
					file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources/data/tv_names.dat')

				words = trie()
				f = open(file_path,'r')
				cnt = 0
				for line in f.readlines():
					words[line.strip().lower()] = None
					cnt += 1
				f.close()
				#

				kb = CustomKeyboard('Custom-DialogKeyboard.xml', os.path.dirname(os.path.realpath(__file__)), category = category, words=words)
				kb.doModal()
				search_string = kb.labelString

				#if nothing was typed, return without doing anything
				if search_string is None or search_string == '' :
					mvl_view_mode = 59
					hide_busy_dialog()
					return None

				url = server_url + "/api/index.php/api/categories_api/searchVideos"

				plugin.log.info(url)
				data = urllib.urlencode({'keywords': '{0}'.format(search_string), 'category': '{0}'.format(category)})
				req = urllib2.Request(url, data)
				plugin.log.info("search url")
				plugin.log.info(data)
				plugin.log.info(url)

				dp = xbmcgui.DialogProgress()

				f = urllib2.urlopen(req)
				response = f.read()
				if response == '0':
					# xbmc.executebuiltin('Notification(Sorry,No Videos Found Matching Your Query,5000,/error.png)')
					showMessage('No result found', 'Sorry, No Videos Found Matching Your Query')
					mvl_view_mode = 59
					hide_busy_dialog()

				else:
					mvl_view_mode = 58
					xbmcplugin.setContent(pluginhandle, 'Movies')

					jsonObj = json.loads(response)
					plugin.log.info(jsonObj)
					items = []
					item_count = len(jsonObj)
					done_count = 0
					dp_created = False
					dp_type = 'show'
					
					for categories in jsonObj:
						if categories['is_playable'] == 'False':
							if categories['top_level_parent'] == '3' and categories['parent_id'] not in ('32', '3'):  # Parsing the TV Shows Titles & Seasons only:		 # if TV Series fetch there fan art
								mvl_meta = ''
								#tmpTitle = categories['title'].encode('utf-8')
								#if tmpTitle == "Season 1":
								#	 tmpSeasons = []
								#	 mvl_view_mode = 50
								#	 # for i in range(totalCats):
								#	 # tmpSeasons.append( i )
								#	 #plugin.log.info('season found')
								#	 #mvl_meta = __metaget__.get_seasons(mvl_tvshow_title, '', tmpSeasons)
								is_season = False
								if 'parent_title' in categories:
									#this must be a TV Show Season list
									mvl_meta = create_meta('tvshow', categories['parent_title'].encode('utf-8'), '', '')
									mvl_tvshow_title = categories['parent_title'].encode('utf-8')
									is_season = True
									#xbmcplugin.setContent(pluginhandle, 'Seasons')

								else:
									mvl_meta = create_meta('tvshow', categories['title'].encode('utf-8'), '', '')
									mvl_tvshow_title = categories['title'].encode('utf-8')

								dp_type = 'show'

								plugin.log.info('meta data-> %s' % mvl_meta)
								thumbnail_url = ''
								try:
									if mvl_meta['cover_url']:
										thumbnail_url = mvl_meta['cover_url']
								except:
									thumbnail_url = ''

								fanart_url = ''
								try:
									if mvl_meta['backdrop_url']:
										fanart_url = mvl_meta['backdrop_url']
								except:
									fanart_url = ''

								mvl_plot = ''
								try:
									if mvl_meta['plot']:
										mvl_plot = mvl_meta['plot']
								except:
									mvl_plot = ''

								if is_season:
									info_dic = {
											'title': categories['title'].encode('utf-8'),
											}
								else:
									info_dic = {
											  'title': categories['title'].encode('utf-8'),
											  'rating': mvl_meta['rating'],
											  'plot': mvl_plot,
											  'year': mvl_meta['year'],
											  'premiered': mvl_meta['premiered'],
											  'duration': mvl_meta['duration']
											  }

								items += [{
											  'label': '{0}'.format(categories['title'].encode('utf-8')),
											  'path': plugin.url_for('get_categories', id=categories['id'], page=0),
											  'is_playable': False,
											  'thumbnail': thumbnail_url,
											  'properties': {
												  'fanart_image': fanart_url,
											  },
											  'info': info_dic,
											  'context_menu': [('','',)],
											  'replace_context_menu': True
										  }]

							else:					 
								items += [{
											  'label': '{0}'.format(categories['title'].encode('utf-8')),
											  'path': plugin.url_for('get_categories', id=categories['id'], page=0),
											  'is_playable': False,
											  'thumbnail': art('{0}.png'.format(categories['title'].lower())),
											  'context_menu': [('','',)],
											  'replace_context_menu': True
										  }]
						elif categories['is_playable'] == 'True':
							categories['title'] = categories['title'].encode('utf-8')
							thumbnail_url = categories['thumbnail']

							dp_type = 'movie'
							
							mvl_img = thumbnail_url
							series_name = 'NONE'

							watch_info = {'video_type': 'movie', 'season': 'NONE', 'episode': 'NONE', 'year': '0'}

							if categories['top_level_parent'] == '1':
								mvl_meta = create_meta('movie', categories['title'], categories['release_date'], mvl_img)
								watch_info['year'] = mvl_meta['year']
							elif categories['top_level_parent'] == '3':
								#playable items of TV show are episodes
								mvl_meta = create_meta('episode', categories['title'], categories['release_date'], mvl_img, categories['sub_categories_names'])
								# mvl_meta = create_meta('movie', categories['title'], '', thumbnail_url)

								watch_info['video_type'] = 'episode'
								watch_info['season'] = mvl_meta['season']
								watch_info['episode'] = mvl_meta['episode']
								watch_info['year'] = mvl_meta['premiered'][:4]

								if watch_info['year'] == '':
									watch_info['year'] = 0

								if 'series_name' in mvl_meta:
									series_name = mvl_meta['series_name'].strip()
								#set layout to Episode
								xbmcplugin.setContent(pluginhandle, 'Episodes')

							plugin.log.info('meta data-> %s' % mvl_meta)
							thumbnail_url = ''
							try:
								if mvl_meta['cover_url']:
									thumbnail_url = mvl_meta['cover_url']
							except:
								thumbnail_url = thumbnail_url
							if thumbnail_url == '':
								thumbnail_url = art('image-not-available.png')

							fanart_url = ''
							try:
								if mvl_meta['backdrop_url']:
									fanart_url = mvl_meta['backdrop_url']
							except:
								fanart_url = ''

							mvl_plot = ''
							try:
								if mvl_meta['plot']:
									mvl_plot = mvl_meta['plot']
							except:
								mvl_plot = categories['synopsis'].encode('utf-8')

							watched_state = 'Watched'
							if mvl_meta['playcount'] > 0:
								watched_state = 'Unwatched'

							items += [{
										  'thumbnail': thumbnail_url,
										  'properties': {
											  'fanart_image': fanart_url,
										  },
										  'label': '{0}'.format(categories['title']),
										  'info': {
											  'title': categories['title'],
											  'rating': categories['rating'],
											  'comment': categories['synopsis'].encode('utf-8'),
											  'Director': categories['director'].encode('utf-8'),
											  'Producer': categories['producer'],
											  'Writer': categories['writer'],
											  'plot': mvl_plot,
											  'genre': categories['sub_categories_names'],
											  #'cast': categories['actors'].encode('utf-8'),
											  'year': categories['release_date'],
											  'premiered': categories['release_date'],
											  'duration': mvl_meta['duration'],
											  'playcount': mvl_meta['playcount']
										  },
										  'path': plugin.url_for('get_videos', id=categories['video_id'],
																 thumbnail=thumbnail_url, trailer=get_trailer_url(mvl_meta).encode('utf-8'),
																 parent_id=categories['top_level_parent'], series_name=series_name),
										  'is_playable': False,
										  'context_menu': [(
															   'Mark as {0}'.format(watched_state),
															   'XBMC.RunPlugin(%s)' % plugin.url_for('mark_as_{0}'.format(watched_state.lower()),
																								 video_type=watch_info['video_type'],
																								 title=categories['title'].encode('utf-8'),
																								 imdb_id=mvl_meta['imdb_id'],
																								 year=watch_info['year'],
																								 season=watch_info['season'],
																								 episode=watch_info['episode']
																									)
														   )],
										  'replace_context_menu': True
									  }]
									  

						if categories['id'] != -1:
							if categories['top_level_parent'] == '1':
								dp_type = 'movie'
							elif categories['top_level_parent'] == '3':
								dp_type = 'show'
									  
						if dp_created == False:
							dp.create("Please wait while "+dp_type+" list is loaded","","")
							dp_created = True
								  
						done_count = done_count + 1
						dp.update((done_count*100/item_count), str(done_count*100/item_count)+"%")

						if dp.iscanceled():
							break								  
							
					dp.close()

					hide_busy_dialog()
					return items
			except IOError:
				# xbmc.executebuiltin('Notification(Unreachable Host,Could not connect to server,5000,/script.hellow.world.png)')
				dialog_msg()
				hide_busy_dialog()
				
			except Exception,e:

				mvl_view_mode = 59
				hide_busy_dialog()
				return None
			
	else:
		mvl_view_mode = 59
		internet_dialog_msg()
		hide_busy_dialog()

@plugin.route('/azlisting/<category>/')
def azlisting(category):
	global mvl_view_mode
	
	if check_internet():
	
		show_notification()	   
		
		mvl_view_mode = 50
		Indices = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
				   'V', 'W', 'X', 'Y', 'Z']
		items = [{
					 'label': '#',
					 'thumbnail': art('hash.png'),
					 'path': plugin.url_for('get_azlist', key='%23', page=0, category=category),
					 'is_playable': False,
				 }]
		for index in Indices:
			items += [{
						  'label': '{0}'.format(index),
						  'thumbnail': art('{0}.png'.format(index)),
						  'path': plugin.url_for('get_azlist', key=index, page=0, category=category),
						  'is_playable': False,
					  }]
					  
		hide_busy_dialog()
		return items
	else:
		mvl_view_mode = 59
		internet_dialog_msg()
		hide_busy_dialog()

@plugin.route('/get_azlist/<key>/<page>/<category>/')
def get_azlist(key, page, category):
	global mvl_view_mode
	mvl_view_mode = 50
	page_limit_az = 200
	
	if check_internet():
	
		show_notification()	   
	
		try:

			dp = xbmcgui.DialogProgress()
		
			url = server_url + "/api/index.php/api/categories_api/getAZList?key={0}&limit={1}&page={2}&category={3}".format(key, page_limit_az, page, category)
			#plugin.log.info("here is the url")
			plugin.log.info(url)
			req = urllib2.Request(url)
			opener = urllib2.build_opener()
			f = opener.open(req)
			content = f.read()
			if content != '0':
				jsonObj = json.loads(content)
				items = []
				item_count = len(jsonObj)
				done_count = 0
				dp_created = False
				dp_type = 'show'
				
				###########
				#if the items are season episodes, we need ot sort them naturally i.e. use Natural Sort for sorting
				if key == '%23':			   
					for results in jsonObj:
						if 'title' not in results:
							results['title'] = '999999999'
						
						title = results['title'].split(' ')[0]
						title_token = ''
						for c in title:
							if c >= '0' and c <= '9':
								title_token += c
							elif c == ',':
								continue
							else:
								break
								
						if title_token == '':
							title_token = '999999999'
						
						if title_token[0] == '0':
							title_token = '0'
						
						results['sort_key'] = title_token
						results['sort_key_len'] = len(title_token)
					
					jsonObj.sort(key=lambda x: (x['sort_key_len'], x['sort_key']))
				
					
				###########

				xbmcplugin.setContent(pluginhandle, 'Movies')

				for results in jsonObj:
					if results['id'] == -1:
						items += [{
									  'label': 'Next >>',
									  'path': plugin.url_for('get_azlist', key=key, page=(int(page) + 1),
															 category=category),
									  'thumbnail': art('next.png'),
									  'is_playable': False,
								  }]
					elif results['is_playable'] == 'False':
						if results['parent_id'] not in ('32', '23'):  # if not Genres then show them
							if results['top_level_parent'] == '3':		# if TV Series fetch there fan art
								mvl_meta = ''
								#tmpTitle = results['title'].encode('utf-8')
								#if tmpTitle == "Season 1":
								#	 tmpSeasons = []
								#	 mvl_view_mode = 50
								#	 # for i in range(totalCats):
								#	 # tmpSeasons.append( i )
								#	 #plugin.log.info('season found')
								#	 #mvl_meta = __metaget__.get_seasons(mvl_tvshow_title, '', tmpSeasons)
								is_season = False
								if 'parent_title' in results:
									#this must be a TV Show Season list
									mvl_meta = create_meta('tvshow', results['parent_title'].encode('utf-8'), '', '')
									mvl_tvshow_title = results['parent_title'].encode('utf-8')
									is_season = True
									#xbmcplugin.setContent(pluginhandle, 'Seasons')


								else:
									mvl_meta = create_meta('tvshow', results['title'].encode('utf-8'), '', '')
									mvl_tvshow_title = results['title'].encode('utf-8')

								dp_type = 'show'

								plugin.log.info('meta data-> %s' % mvl_meta)
								thumbnail_url = ''
								try:
									if mvl_meta['cover_url']:
										thumbnail_url = mvl_meta['cover_url']
								except:
									thumbnail_url = ''

								fanart_url = ''
								try:
									if mvl_meta['backdrop_url']:
										fanart_url = mvl_meta['backdrop_url']
								except:
									fanart_url = ''

								mvl_plot = ''
								try:
									if mvl_meta['plot']:
										mvl_plot = mvl_meta['plot']
								except:
									mvl_plot = ''

								if is_season:
									info_dic = {
											'title': results['title'].encode('utf-8'),
											}
								else:
									info_dic = {
											  'title': results['title'].encode('utf-8'),
											  'rating': mvl_meta['rating'],
											  'plot': mvl_plot,
											  'year': mvl_meta['year'],
											  'premiered': mvl_meta['premiered'],
											  'duration': mvl_meta['duration']
											  }

								items += [{
											  'label': '{0}'.format(results['title'].encode('utf-8')),
											  'path': plugin.url_for('get_categories', id=results['id'], page=0),
											  'is_playable': False,
											  'thumbnail': thumbnail_url,
											  'properties': {
												  'fanart_image': fanart_url,
											  },
											  'info': info_dic,
											  'context_menu': [('','',)],
											  'replace_context_menu': True
										  }]

							else:
								items += [{
											  'label': '{0}'.format(results['title'].encode('utf-8')),
											  'path': plugin.url_for('get_categories', id=results['id'], page=0),
											  'is_playable': False,
											  'thumbnail': art('{0}.png'.format(results['title'].lower())),
											  'context_menu': [('','',)],
											  'replace_context_menu': True
										  }]

					elif results['is_playable'] == 'True':
						results['title'] = results['title'].encode('utf-8')
						thumbnail_url = results['thumbnail']

						dp_type = 'movie'

						mvl_img = thumbnail_url
						series_name = 'NONE'

						watch_info = {'video_type': 'movie', 'season': 'NONE', 'episode': 'NONE', 'year': ''}

						if results['top_level_parent'] == '1':
							mvl_meta = create_meta('movie', results['title'], results['release_date'], mvl_img)
							watch_info['year'] = mvl_meta['year']
						elif results['top_level_parent'] == '3':
							#playable items of TV show are episodes
							mvl_meta = create_meta('episode', results['title'], results['release_date'], mvl_img, results['sub_categories_names'])
							# mvl_meta = create_meta('movie', results['title'], '', thumbnail_url)

							watch_info['video_type'] = 'episode'
							watch_info['season'] = mvl_meta['season']
							watch_info['episode'] = mvl_meta['episode']
							watch_info['year'] = mvl_meta['premiered'][:4]

							if watch_info['year'] == '':
								watch_info['year'] = 0

							if 'series_name' in mvl_meta:
								series_name = mvl_meta['series_name'].strip()
							#set layout to Episode
							xbmcplugin.setContent(pluginhandle, 'Episodes')

						plugin.log.info('meta data-> %s' % mvl_meta)
						thumbnail_url = ''
						try:
							if mvl_meta['cover_url']:
								thumbnail_url = mvl_meta['cover_url']
						except:
							thumbnail_url = thumbnail_url

						fanart_url = ''
						try:
							if mvl_meta['backdrop_url']:
								fanart_url = mvl_meta['backdrop_url']
						except:
							fanart_url = ''

						mvl_plot = ''
						try:
							if mvl_meta['plot']:
								mvl_plot = mvl_meta['plot']
						except:
							mvl_plot = results['synopsis'].encode('utf-8')

						watched_state = 'Watched'
						if mvl_meta['playcount'] > 0:
							watched_state = 'Unwatched'

						items += [{
									  'thumbnail': thumbnail_url,
									  'properties': {
										  'fanart_image': fanart_url,
									  },
									  'label': '{0}'.format(results['title']),
									  'info': {
										  'title': results['title'],
										  'rating': results['rating'],
										  'comment': results['synopsis'].encode('utf-8'),
										  'Director': results['director'].encode('utf-8'),
										  'Producer': results['producer'],
										  'Writer': results['writer'],
										  'plot': mvl_plot,
										  'genre': results['sub_categories_names'],
										  #'cast': results['actors'].encode('utf-8'),
										  'year': results['release_date'],
										  'premiered': results['release_date'],
										  'duration': mvl_meta['duration']

									  },
									  'path': plugin.url_for('get_videos', id=results['video_id'],
															 thumbnail=results['thumbnail'], trailer=get_trailer_url(mvl_meta).encode('utf-8'),
															 parent_id=results['top_level_parent'], series_name=series_name),
									  'is_playable': False,
									  'context_menu': [(
														   'Mark as {0}'.format(watched_state),
														   'XBMC.RunPlugin(%s)' % plugin.url_for('mark_as_{0}'.format(watched_state.lower()),
																								 video_type=watch_info['video_type'],
																								 title=results['title'],
																								 imdb_id=mvl_meta['imdb_id'],
																								 year=watch_info['year'],
																								 season=watch_info['season'],
																								 episode=watch_info['episode']
																							   )
													   )],
									  'replace_context_menu': True
								  }]

					if results['id'] != -1:
						if results['top_level_parent'] == '1':
							dp_type = 'movie'
						elif results['top_level_parent'] == '3':
							dp_type = 'show'
						
					if dp_created == False:
						dp.create("Please wait while "+dp_type+" list is loaded","","")
						dp_created = True
								  
					done_count = done_count + 1
					dp.update((done_count*100/item_count), str(done_count*100/item_count)+"%")

					if dp.iscanceled():
						break
					
				# plugin.log.info('itemcheck')
				# plugin.log.info(items)
				
				dp.close()
				
				hide_busy_dialog()
				return items
			else:
				# xbmc.executebuiltin('Notification(Sorry,No Videos Available In this Category,5000,/error.png)')
				showMessage('No result found', 'Sorry, No Videos Available In this Category')
				hide_busy_dialog()
		except IOError:
			# xbmc.executebuiltin('Notification(Unreachable Host,Could not connect to server,5000,/script.hellow.world.png)')
			dialog_msg()
			hide_busy_dialog()
			
	else:
		mvl_view_mode = 59
		internet_dialog_msg()
		hide_busy_dialog()

@plugin.route('/mostpopular/<page>/<category>/')
def mostpopular(page, category):
	global mvl_view_mode
	mvl_view_mode = 50
	try:

		dp = xbmcgui.DialogProgress()
		
		page_limit_mp = 30
	
		url = server_url + "/api/index.php/api/categories_api/getMostPopular?limit={0}&page={1}&category={2}".format(page_limit_mp, page, category)
		plugin.log.info(url)
		req = urllib2.Request(url)
		opener = urllib2.build_opener()
		f = opener.open(req)
		content = f.read()
		if content != '0':
			jsonObj = json.loads(content)
			items = []
			item_count = len(jsonObj)
			done_count = 0
			dp_created = False
			dp_type = 'show'

			for results in jsonObj:
				if results['id'] == -1:
					items += [{
								  'label': 'Next >>',
								  'path': plugin.url_for('mostpopular', page=(int(page) + 1)),
								  'is_playable': False,
							  }]
				else:
					if results['source'] == '1':
						thumbnail_url = results['image_name']
					else:
						thumbnail_url = server_url + '/wp-content/themes/twentytwelve/images/{0}'.format(
							results['id'] + results['image_name'])

					results['title'] = results['title'].encode('utf-8')

					dp_type = 'movie'

					mvl_meta = create_meta('movie', results['title'], results['release_date'], thumbnail_url)
					plugin.log.info('meta data-> %s' % mvl_meta)
					thumbnail_url = ''
					try:
						if mvl_meta['cover_url']:
							thumbnail_url = mvl_meta['cover_url']
					except:
						thumbnail_url = thumbnail_url

					fanart_url = ''
					try:
						if mvl_meta['backdrop_url']:
							fanart_url = mvl_meta['backdrop_url']
					except:
						fanart_url = ''
					items += [{
								  'label': '{0}'.format(results['title']),
								  'thumbnail': thumbnail_url,
								  'properties': {
									  'fanart_image': fanart_url,
								  },
								  'path': plugin.url_for('get_videos', id=results['id'],
														 thumbnail=thumbnail_url, trailer=get_trailer_url(mvl_meta).encode('utf-8'),
														 parent_id=results['top_level_parent']),
								  'is_playable': False,
								  'context_menu': [(
													   'Mark as Watched',
													   'XBMC.RunPlugin(%s)' % plugin.url_for('save_favourite',
																							 id=results['id'],
																							 title=results['title'],
																							 thumbnail=thumbnail_url,
																							 isplayable="True",
																							 category=category)
												   )],
								  'replace_context_menu': True
							  }]

				if results['id'] != -1:
					if results['top_level_parent'] == '1':
						dp_type = 'movie'
					elif results['top_level_parent'] == '3':
						dp_type = 'show'
					
				if dp_created == False:
					dp.create("Please wait while "+dp_type+" list is loaded","","")
					dp_created = True
							  
				done_count = done_count + 1
				dp.update((done_count*100/item_count), str(done_count*100/item_count)+"%")

				if dp.iscanceled():
					break
			
			dp.close()
			
			hide_busy_dialog()
			return items
		else:
			# xbmc.executebuiltin('Notification(Sorry,No Videos Available In this Category,5000,/error.png)')
			showMessage('No result found', 'Sorry, No Videos Available In this Category')
			hide_busy_dialog()
	except IOError:
		# xbmc.executebuiltin('Notification(Unreachable Host,Could not connect to server,5000,/script.hellow.world.png)')
		dialog_msg()
		hide_busy_dialog()

def init_database():
	plugin.log.info('Building My Video Library Database')
	if not xbmcvfs.exists(os.path.dirname(DB_DIR)):
		xbmcvfs.mkdirs(os.path.dirname(DB_DIR))
	db = orm.connect(DB_DIR)
	db.execute(
		'CREATE TABLE IF NOT EXISTS favourites (id, title, thumbnail, isplayable, category, PRIMARY KEY (id, title, category))')
	db.commit()
	db.close()


@plugin.route('/mark_as_watched/<video_type>/<title>/<imdb_id>/<season>/<episode>/<year>')
def mark_as_watched(video_type, title, imdb_id, season, episode, year):
	if video_type == 'movie':
		__metaget__.change_watched(video_type, title, imdb_id, season=None, episode=None, year=year, watched=7)
	elif video_type == 'episode':
		__metaget__.change_watched(video_type, title, imdb_id, season=season, episode=episode, year=year, watched=7)

	xbmc.executebuiltin("XBMC.Container.Refresh")

@plugin.route('/mark_as_unwatched/<video_type>/<title>/<imdb_id>/<season>/<episode>/<year>')
def mark_as_unwatched(video_type, title, imdb_id, season, episode, year):
	if video_type == 'movie':
		__metaget__.change_watched(video_type, title, imdb_id, season=None, episode=None, year=year, watched=6)
	elif video_type == 'episode':
		__metaget__.change_watched(video_type, title, imdb_id, season=season, episode=episode, year=year, watched=6)

	xbmc.executebuiltin("XBMC.Container.Refresh")


def sys_exit():
	hide_busy_dialog()
	# plugin.finish(succeeded=True)
	xbmc.executebuiltin("XBMC.ActivateWindow(Home)")

	#reset path to home
	file_write('screen_path.dat', None)


@plugin.route('/get_favourites/<category>/')
def get_favourites(category):
	global mvl_view_mode
	mvl_view_mode = 50
	statement = 'SELECT * FROM favourites WHERE category = "%s"' % category
	plugin.log.info(statement)
	db = orm.connect(DB_DIR)
	cur = db.cursor()
	cur.execute(statement)
	favs = cur.fetchall()
	items = []
	plugin.log.info(favs)
	for row in favs:
		plugin.log.info(row[0])
		if row[3] == 'False':
			items += [{
						  'label': '{0}'.format(row[1]),
						  'thumbnail': row[2],
						  'path': plugin.url_for('get_categories', id=row[0], page=0),
						  'is_playable': False,
						  'context_menu': [(
											   'Remove from Favourites',
											   'XBMC.RunPlugin(%s)' % plugin.url_for('remove_favourite', id=row[0],
																					 title=row[1], category=row[4])
										   )],
						  'replace_context_menu': True
					  }]
		elif row[3] == 'True':
			items += [{
						  'label': '{0}'.format(row[1]),
						  'thumbnail': row[2],
						  'path': plugin.url_for('get_videos', id=row[0], thumbnail=row[2]),
						  'is_playable': False,
						  'context_menu': [(
											   'Remove from Favourites',
											   'XBMC.RunPlugin(%s)' % plugin.url_for('remove_favourite', id=row[0],
																					 title=row[1], category=row[4])
										   )],
						  'replace_context_menu': True
					  }]
	db.close()
	hide_busy_dialog()
	return items



class CustomTermsPopup(xbmcgui.WindowXMLDialog):
	def __init__(self, xmlFilename, scriptPath, defaultSkin = "Default", defaultRes = "1080i"):
		pass

	def updateTermText(self, heading, term_text):
		self.show()
		self.getControl(1).setLabel(heading)
		self.getControl(2).setText(term_text)

		self.close()

	def onClick	(self, control):
		if control == 11:
			self.close()
			onClick_agree()
		elif control == 10:
			self.close()
			onClick_disAgree()


class CustomPopup(xbmcgui.WindowXMLDialog):
	def __init__(self, xmlFilename, scriptPath, defaultSkin = "Default", defaultRes = "1080i"):
		pass

	def setParams(self, trailer_id, source_url, resolved_url, title, video_id, series_id, mvl_meta):
		self.trailer_id = trailer_id
		self.trailer_url = 'http://www.youtube.com/watch?v='+trailer_id
		self.source_url = source_url
		self.resolved_url = resolved_url
		self.title = title.strip()
		self.video_id = video_id
		self.series_id = series_id
		self.meta = mvl_meta

		if trailer_id == 'NONE' and series_id != 'NONE':
			self.video_type = 'episode'
		else:
			self.video_type = 'movie'

	def updateLabels(self):
		self.show()
		self.getControl(20).setLabel(self.source_url)
		self.close()

	def onClick	(self, control):
		if control == 20:
			#show source URL
			# showMessage('Msg', self.trailer_url)
			pass
		elif control == 21:
			#play trailer
			self.close()

			if self.trailer_id == 'NONE':
				showMessage('Error', 'No trailer found')
				resume_popup_window()
			else:
				play_video(self.trailer_url, 'NONE', self.title + ' - Official trailer', self.video_type, self.meta)


		elif control == 22:
			self.close()
			play_video(self.source_url, self.resolved_url, self.title, self.video_type, self.meta)

		elif control == 23:
			#exit

			#clear path of current popup
			file_write('screen_path.dat', None)

			self.close()

		elif control == 24:
			self.close()
			show_review(self.video_id)

		elif control == 18:
			#other viewing options
			self.close()

			purchase_dialog = CustomPurchaseOptions('Custom-PurchaseOptions.xml', os.path.dirname(os.path.realpath(__file__)))
			purchase_dialog.showDialog()

			resume_popup_window()

		elif control == 28:
			#official posters
			self.close()

			if self.trailer_id == "NONE":
				poster_text = "For Official posters and images, please visit: [COLOR FF1F6C15] http://thetvdb.com/?tab=seriesposters&id="+self.series_id+"[/COLOR]"
			else:
				poster_text = "For Official posters and images, please visit: [COLOR FF1F6C15] http://www.themoviedb.org/movie/"+self.series_id+"-"+self.title.replace(' ', '-')+"/backdrops [/COLOR]"

			dialog = xbmcgui.Dialog()
			dialog.ok("Posters & Images", poster_text)

			resume_popup_window()

		elif control == 15:
			#Watch Previews
			self.close()

			dialog = xbmcgui.Dialog()
			dialog.ok("Watch Previews", "Please visit http://www.primetvseries.com to watch previews of your favorite shows")

			resume_popup_window()

		elif control == 16:
			#Watch Previews
			self.close()

			dialog = xbmcgui.Dialog()
			dialog.ok("Read Reviews", "Please visit http://www.metacritic.com/tv to read reviews of your favorite shows")

			resume_popup_window()

		elif control == 29:
			#facebook share
			#self.close()
			pass


class CustomReviewPopup(xbmcgui.WindowXMLDialog):
	def __init__(self, xmlFilename, scriptPath, defaultSkin = "Default", defaultRes = "1080i"):
		pass

	def setParams(self, review_url):
		self.review_url = review_url

	def updateReviewText(self, review, critic_name, review_publish_date, heading):
		self.show()
		#self.getControl(1).setLabel(heading+'\n[COLOR FF888888] By '+critic_name+' ('+review_publish_date+') [/COLOR]')
		self.getControl(1).setLabel(heading)
		self.getControl(4).setLabel('[COLOR FF888888] By '+critic_name+' ('+review_publish_date+', The New York Times) [/COLOR]')
		self.getControl(2).setText(review)

		self.close()

	def onClick	(self, control):
		if control == 11:
			self.close()
			resume_popup_window()


class CustomPurchaseOptions(xbmcgui.WindowXMLDialog):
	def __init__(self, xmlFilename, scriptPath, defaultSkin = "Default", defaultRes = "1080i"):
		pass

	def showDialog(self):
		self.show()
		self.getControl(21).setLabel("Purchase & Viewing")
		self.getControl(22).setLabel("Amazon.com .................. [COLOR FF1F6C15]www.amazon.com/dvd[/COLOR]")
		self.getControl(23).setLabel("Google Play ................... [COLOR FF1F6C15]www.play.google.com/store/movies[/COLOR]")
		self.getControl(24).setLabel("iTunes.com ..................... [COLOR FF1F6C15]www.apple.com/itunes/charts/movies[/COLOR]")
		self.getControl(25).setLabel("Fandango ....................... [COLOR FF1F6C15]www.fandango.com[/COLOR]")
		self.close()

		self.doModal()

	def onClick	(self, control):
		if control == 10:
			self.close()


class CustomKeyboard(xbmcgui.WindowXMLDialog):
	def __init__(self, xmlFilename, scriptPath, category, words, defaultSkin = "Default", defaultRes = "1080i"):
		self.isUpper  = 0
		self.isSymbol = 0
		self.isLock	  = 0
		self.show()
		self.category = category
		#print self.category
		self.cursorState = 1
		self.cursorPos	 = 0
		self.labelString = None
		self.updateKeyboardLabel()
		self.words = words

	def showCursor(self):
		if self.isLock == 1:
			time.sleep(.1)

		label = self.getControl(310).getLabel()
		labelList = list(str(label))
		if self.cursorState == 0:
			labelList[self.cursorPos] = '|'
			self.cursorState = 1
		else:
			labelList[self.cursorPos] = ' '
			self.cursorState = 0
		label = ''.join(labelList)
		self.getControl(310).setLabel(label)
		time.sleep(.4)
		self.showCursor()

	def updateKeyboardLabel(self):

		self.getControl(311).setLabel("Search Media Engine")
		self.getControl(310).setLabel("|")
		for i in range(434, 439):
			self.getControl(i).setVisible(False)
		self.updateKeyboardLabelToLowerCase()
		self.updateKeyboardLabelNumeric()

		#self.t = Thread(target = testThread)
		# time.sleep()
		self.t = Thread(name='test', target=self.showCursor)
		self.t.daemon = True
		self.t.start()

	def updateKeyboardLabelNumeric(self):
		self.isLock = 0;
		for i in range(48, 58):
			try:
				self.getControl(i).setLabel(chr(i))
			except:
				pass

	def updateKeyboardLabelToLowerCase(self):
		self.isLock = 0;
		self.isUpper  = 0
		for i in range(0, 27):
			try:
				self.getControl(i+65).setLabel(chr(i+97))
			except:
				pass

	def updateKeyboardLabelToUpperCase(self):
		self.isUpper  = 1
		for i in range(0, 27):
			try:
				self.getControl(i+65).setLabel(chr(i+65))
			except:
				pass

	def updateKeyboardLabelSymbols(self):
		keys = "QWERTYUIOPASDFGHJKLZXCVBNM"
		symbols = "!@#$%^&*()_-+[]|\\:;'<>?/.,"

		for i in range(0, len(keys)):
			try:
				self.getControl(ord(keys[i])).setLabel(symbols[i])
			except:
				pass

	def findSymbol(self, control):
		ret = ''
		if self.isSymbol != 1:
			ret = chr(control)
			if(self.isUpper == 0):
				ret = ret.lower()
		else:
			keys = "QWERTYUIOPASDFGHJKLZXCVBNM"
			symbols = "!@#$%^&*()_-+[]|\\:;'<>?/.,"
			ret = chr(control)
			pos = keys.find(ret)
			ret = symbols[pos]
		return ret

	def updateSuggestion(self):
		#return
		for i in range(434, 439):
			self.getControl(i).setVisible(False)
			self.getControl(i).setLabel('')
		label = self.getControl(310).getLabel()
		labelList = list(label)
		del labelList[self.cursorPos]
		if(len(labelList) == 0):
			return
		label = ''.join(labelList)
		label = label.lower()
		control = 434

		#r = requests.get('http://config.myvideolibrary.com/api/index.php/api/categories_api/getAZList?key=A&page=0&category=3&limit=5')
		#print r.text
		sugg = self.words.iter(label)
		cnt = 0
		for word in sugg:
			if control > 438:
				break
			self.getControl(control).setLabel(word)
			self.getControl(control).setVisible(True)
			control += 1
		return

	def moveLeft(self):
		self.isLock = 1
		label = self.getControl(310).getLabel()
		if(self.cursorPos == 0):
			self.isLock = 0
			return
		labelList = list(label)
		#print "{0}, {1}, {2}".format(self.cursorPos, label, len(label))
		del labelList[self.cursorPos]
		self.cursorPos -= 1
		if(self.cursorPos < 0):
			self.cursorPos = 0
		newLabelList = []
		for i in range(0, self.cursorPos):
			newLabelList.append(labelList[i])
		newLabelList.append(' ')
		for i in range(self.cursorPos, len(labelList)):
			newLabelList.append(labelList[i])
		if self.cursorState == 1:
			newLabelList[self.cursorPos] = '|'
			self.cursorState = 1
		else:
			newLabelList[self.cursorPos] = ' '
			self.cursorState = 0
		label = ''.join(newLabelList)
		self.getControl(310).setLabel(label)
		self.updateSuggestion()
		self.isLock = 0
		return

	def moveRight(self):
		self.isLock = 1
		label = self.getControl(310).getLabel()
		if(self.cursorPos == len(label)-1):
			self.isLock = 0
			return
		labelList = list(label)
		#self.cursorPos += 1
		#if(self.cursorPos >= len(label)):
		#	 self.cursorPos = len(label)-1


		#print "{0}, {1}, {2}".format(self.cursorPos, label, len(label))
		del labelList[self.cursorPos]
		newLabelList = []
		for i in range(0, self.cursorPos+1):
			newLabelList.append(labelList[i])
		newLabelList.append(' ')
		for i in range(self.cursorPos+1, len(labelList)):
			newLabelList.append(labelList[i])
		self.cursorPos += 1
		if(self.cursorPos >= len(label)-1):
			self.cursorPos = len(label)-1
		if self.cursorState == 1:
			newLabelList[self.cursorPos] = '|'
			self.cursorState = 1
		else:
			newLabelList[self.cursorPos] = ' '
			self.cursorState = 0
		label = ''.join(newLabelList)
		self.getControl(310).setLabel(label)
		self.isLock = 0
		return

	def deleteChar(self):
		self.isLock = 1
		if self.cursorPos == 0:
			self.isLock = 0
			return
		label = self.getControl(310).getLabel()
		labelList = list(label)
		#print "{0}, {1}, {2}".format(self.cursorPos, label, len(label))
		del labelList[self.cursorPos-1]
		#sym = self.findSymbol(control)
		#labelList += list(sym)
		self.cursorPos -= 1
		if(self.cursorPos < 0):
			self.cursorPos = 0
		#print self.cursorPos
		if self.cursorState == 1:
			labelList[self.cursorPos] = '|'
			self.cursorState = 1
		else:
			labelList[self.cursorPos] = ' '
			self.cursorState = 0
		label = ''.join(labelList)
		self.getControl(310).setLabel(label)
		self.updateSuggestion()
		self.isLock = 0
		return

	def insertChar(self, sym):
		self.isLock = 1
		#print self.words.__len__()
		label = self.getControl(310).getLabel()
		labelList = list(label)
		#print "{0}, {1}, {2}".format(self.cursorPos, label, len(label))
		#del labelList[self.cursorPos]
		newLabelList = []
		for i in range(0, self.cursorPos):
			newLabelList.append(labelList[i])
		newLabelList += list(sym)
		for i in range(self.cursorPos, len(labelList)):
			newLabelList.append(labelList[i])
		#labelList.append('')
		self.cursorPos += len(sym)
		#print self.cursorPos
		if self.cursorState == 1:
			newLabelList[self.cursorPos] = '|'
			self.cursorState = 1
		else:
			newLabelList[self.cursorPos] = ' '
			self.cursorState = 0
		label = ''.join(newLabelList)
		self.getControl(310).setLabel(label)
		self.updateSuggestion()
		self.isLock = 0
		return

	def onAction(self, action):
		if action.getId() != 100 and action.getId() != 107:
			v = action.getButtonCode() & 255
			if v >= 33 and v <= 126: #ascii
				v = chr(v)
				if self.isUpper == 0:
					v = v.lower()
				self.insertChar(v)
			elif v == 8: #backspace
				self.deleteChar()
			elif v == 130: #left
				self.moveLeft()
			elif v == 131: #right
				self.moveRight()
			elif v == 13: #enter
				label = self.getControl(310).getLabel()
				labelList = list(label)
				#print "{0}, {1}, {2}".format(self.cursorPos, label, len(label))
				del labelList[self.cursorPos]
				self.labelString = ''.join(labelList)
				self.close()
				pass
			elif v == 27:
				self.labelString = ''
				self.close()
				pass
			elif v == 32:
				self.insertChar(' ')
			else:
				pass

			#print "muri "+ str(v)
			# 8 back, 9 tab, 13 enter, esc 27, left 130, right 131
			''''''
		pass

	def onClick (self, control):
		#print "control test"
		if control == 300:
			label = self.getControl(310).getLabel()
			labelList = list(label)
			#print "{0}, {1}, {2}".format(self.cursorPos, label, len(label))
			del labelList[self.cursorPos]
			self.labelString = ''.join(labelList)
			self.close()
			return
		if control == 301:
			self.labelString = ''
			self.close()
			return


		''' This Thing is needed to be done '''
		if control == 305:
			self.moveLeft()
			return


		if control == 306:
			self.moveRight()
			return

		if control == 8: #Del/ Backspace
			self.deleteChar()
			return

		if control == 303 or control == 302:
			if self.isSymbol != 1:
				if self.isUpper==0:
					self.updateKeyboardLabelToUpperCase()
				else:
					self.updateKeyboardLabelToLowerCase()
			else:
				if self.isUpper == 0:
					self.isUpper = 1
				else:
					self.isUpper = 0
			return
		if control == 304:
			if self.isSymbol == 1:
				self.isSymbol = 0
				if self.isUpper == 1:
					self.updateKeyboardLabelToUpperCase()
				else:
					self.updateKeyboardLabelToLowerCase()
			else:
				self.isSymbol = 1
				self.updateKeyboardLabelSymbols()
			return

		# suggestions buttons
		if control >= 434 and control <= 438:
			self.isLock = 1
			self.labelString = self.getControl(control).getLabel()
			#label += "|"
			#self.cursorPos = len(label)-1

			'''self.getControl(310).setLabel(label)

			for i in range(434, 439):
				self.getControl(i).setVisible(False)
				self.getControl(i).setLabel('')
			'''

			self.close()

			self.isLock = 0
			return

		self.insertChar(self.findSymbol(control))



if __name__ == '__main__':
	plugin.run()
	#xbmc.executebuiltin("Container.SetViewMode(%s)" % 50)
	time.sleep(0.1)
	xbmc.executebuiltin("Container.SetViewMode(%s)" % mvl_view_mode)

	####
	last_path = file_read('screen_path.dat')

	if last_path and 'mark_as' not in last_path:
		#do not update path in case of mark_as_watched/unwatched was selected
		path = xbmc.getInfoLabel('Container.FolderPath')
		file_write('screen_path.dat', path)





