from xbmcswift2 import Plugin, xbmcgui, xbmc, xbmcaddon, xbmcplugin, actions
from pyxbmct.addonwindow import *

import urllib2
import time
import simplejson as json
import urllib
import urllib2
import urlresolver
import xbmcvfs
import xbmcaddon
import xbmcplugin
from t0mm0.common.addon import Addon
#import re
import sys
import os
#import resources.htmlcleaner
import traceback
from metahandler import metahandlers
from metahandler import metacontainers

print 'HERE NOW'

_MVL = Addon('plugin.video.mvl', sys.argv)
plugin = Plugin()
pluginhandle = int(sys.argv[1])
usrsettings = xbmcaddon.Addon(id='plugin.video.mvl')
page_limit = usrsettings.getSetting('page_limit_xbmc')
authentication = plugin.get_storage('authentication', TTL=1)
authentication['logged_in'] = 'false'
username = usrsettings.getSetting('username_xbmc')
activation_key = usrsettings.getSetting('activationkey_xbmc')
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
# cache = StorageServer.StorageServer("plugin://plugin.video.mvl/", 24)
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
mvl_view_mode = 59
mvl_tvshow_title = ''
isAgree = False


@plugin.route('/')
def index():
    global Main_cat
    global mvl_view_mode

    try:
    
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'userdata', 'advancedsettings.xml')
        found = False
        if os.path.exists(file_path):
            file = open(file_path, 'r')
            for line in file:
                if '<showparentdiritems>false</showparentdiritems>' in line:
                    found = True
            file.close()
            
        if not found:
            file = open(file_path, 'w')
            file.write('<advancedsettings>\n')
            file.write('<filelists>\n')
            file.write('<showparentdiritems>false</showparentdiritems>\n')
            file.write('</filelists>\n')
            file.write('<lookandfeel>\n')
            file.write('<skin>skin.mvl</skin>\n')
            file.write('</lookandfeel>\n')
            file.write('</advancedsettings>\n')
            file.close()
            xbmc.executebuiltin('RestartApp')
            return
    
        # Create a window instance.
        #global isAgree
        check_condition()
        #creating the database if not exists
        mvl_view_mode = 58
        init_database()
        #creating a context menu
        #url used to get main categories from server
        url = server_url + "/api/index.php/api/categories_api/getCategories?parent_id=0&limit={0}&page=1".format(
            page_limit)
        plugin.log.info(url)
        req = urllib2.Request(url)
        opener = urllib2.build_opener()
        f = opener.open(req)
        #reading content fetched from the url
        content = f.read()
        #converting to json object
        jsonObj = json.loads(content)
        items = []

        if isAgree == True:
            plugin.log.info("here is dialog")
            #creating items from json object
            for categories in jsonObj:
                items += [{
                              'label': '{0}'.format(categories['title']),
                              'path': plugin.url_for('get_categories', id=categories['id'], page=0),
                              'is_playable': False,
                              'thumbnail': art('{0}.png'.format(categories['title'].lower())),
                          }]
            return items

    except IOError:
        xbmc.executebuiltin('Notification(Unreachable Host,Could not connect to server,5000,/error.png)')


def onClick_disAgree():
    window.close()
    sys_exit()


def onClick_agree():
    global isAgree
    macAddress = usrsettings.getSetting('mac_address')
    plugin.log.info("I Agree func calls")
    url = server_url + "/api/index.php/api/authentication_api/set_flag_status?username={0}&mac={1}".format(username,
                                                                                                           macAddress)
    req = urllib2.Request(url)
    opener = urllib2.build_opener()
    f = opener.open(req)

    isAgree = True
    window.close()


def next_page():
    global curr_page
    if curr_page == 1:
        window.textbox.setText(
            "Relationship\nThe relationship between you (the user) and us (MVL) is that we provide you with access to the referencing material and media contained within our site, which is provided to you on a purely non commercial basis and is, therefore, not that of customer and supplier.\nContent\nOther than descriptive material about the movies, MVL does not host, provide, archive, store, or distribute media of any kind, and acts merely as an index (or directory) of media posted by other webmasters on the internet, which is completely outside of our control. In general, we cannot and do not attempt to control, censor, or block any indexed material that may be considered offensive, abusive, libelous, obnoxious, inaccurate, deceptive, unlawful or otherwise distressing and neither do we accept responsibility for this content or the consequences of such content being made available.  Sometimes we do block referenced material because a third party asserts superior rights or for other legitimate reasons.  We are not responsible for your use of referenced material or your access to referenced material. ")
        plugin.log.info("clicked")
        curr_page = 2
    elif curr_page == 2:
        window.textbox.setText(
            "Material may be inappropriately described or subject to restrictions such as copyright, licensing and other limitations and it is the sole responsibility of those having access to such material to comply with any or all lawful obligations arising from such material coming into their possession and, thus mitigate any alleged transgression. All users warrant that they are 18 years of age or older, and, therefore, qualified to enter into this agreement either as an individual or as a corporate entity. All users undertake to comply with applicable laws and observe the rights inherent in any copyright material whilst upholding the rights of any copyright owner. All users are advised to use caution, discretion, common sense and personal judgment when using My Video Library.com or any references detailed within the directory and to respect the wishes of others who may value freedom, as consenting adults equal to (or possibly superior to) your own personal preferences.\nQuality Of Service\nMVL does not provide commercial services and there are no actual or implied guarantees as to the availability of service or the speed, operation or function of this website, which is offered on a basis to those who choose to comply with the terms and conditions detailed within and access the \'free\' content of this website.")
        plugin.log.info("clicked")
        curr_page = 3
    elif curr_page == 3:
        window.textbox.setText(
            "SOME JURISDICTIONS PROVIDE FOR CERTAIN WARRANTIES, LIKE THE IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. TO THE EXTENT PERMITTED BY LAW, WE EXCLUDE ALL WARRANTIES. \nIndemnification.\nYou, as a user of the website, agree to indemnify, defend, and hold MVL harmless from any and all liability, claims, actions, expenses (including attorneys\' fees and costs) that MVL may have relating to or arising from (a) your use of (or consequences of your use of) the website, or (b) any allegation that your use of the referenced material violates the trademark, copyright or other intellectual property rights of any third party.\nPrivacy\nThis website will comply with the requirements of any law enforcement or other officials, courts, or others with a legitimate interest in the official investigation or enforcement of applicable law.\nThe protection of the rights of others is important to MVL, and this extends to your adherence to intellectual property law, the rights of others to enjoy freedom from slander, libel, defamation, provocation, harassment, discrimination of any kind or any other action that may be deemed offensive by the individual concerned.")
        plugin.log.info("clicked")
        curr_page = 4
    elif curr_page == 4:
        window.textbox.setText(
            "MVL is committed to protecting your privacy. MVL does not sell, trade or rent your personal information to any other companies. MVL will not collect any personal information about you except when you specifically and knowingly provide such information when registering for the website.\nBy using our website, you consent to the collection and use of this information by MVL. If we decide to change our privacy policy, we will post any changes to this page so that you are aware of which information we collect, how we use it, and under which circumstances we disclose it.\nIntellectual Property - General\nMVL respects the rights of others, and prohibits the use of referenced material for any purpose other than that for which it is intended (where such use is lawful and free of civil liability or other constraint) and in such circumstances where possession of such material may have any adverse financial, prejudicial or any other effect on any other third party.\nIf you believe in good faith your work has been copied in a way that constitutes copyright infringement, or that your intellectual property rights have been otherwise violated, please provide the following to MVL\'s Copyright Agent:\nA description of the copyrighted work or intellectual property that you claim has been infringed, or if multiple works, a listing of such works.")
        plugin.log.info("clicked")
        curr_page = 5
    elif curr_page == 5:
        window.textbox.setText(
            "Identification of the referenced material that is claimed to be infringing or to be the subject of infringing activity and that is to be removed or access to which is to be disabled, and information reasonably sufficient to permit MVL to locate the referenced material;\nInformation reasonably sufficient for MVL to contact you: name, address, phone number and email address;\nA statement, made by you, that you have a good faith belief that the disputed use of the material is not authorized by the copyright owner, its agent or the law;\nA statement by you, made under penalty of perjury, that the information in your notice is accurate and that you are the copyright owner or authorized to act on the copyright owner\'s behalf;\nA physical or electronic signature of the copyright owner, or a person authorized to act on behalf of the owner of an exclusive right that is allegedly infringed.\nMVL\'s Copyright Agent can be contacted as follows:\nBy Mail:\nMy Video Library, Inc.\nAttn: Copyright Agent\n401 E. Las Olas Blvd. Suite 1400\nFort. Lauderdale, Fl. 33301")
        plugin.log.info("clicked")
        curr_page = 6
    elif curr_page == 6:
        window.textbox.setText(
            "By Electronic Mail:\ncopyright@MyVideoLibrary.com\nBy Phone:\n800.380.5991\nPlease address all notices to the \'Copyright Agent\' and write \'Copyright Notice\' in the subject line.\nGoverning Law\nFlorida law governs this Conditions of Use agreement without regard to the its conflicts of law provisions. You agree that all claims and legal proceedings arising in connection with the use of the website will be brought solely in the federal or state courts located in Broward County, Florida, United States, and you consent to the jurisdiction of and venue in such courts and waive any objection as to inconvenient forum.\nLast updated October 15, 2013\n")
        plugin.log.info("clicked")


def prev_page():
    global curr_page
    if curr_page == 2:
        window.textbox.setText(
            "General\nWelcome to My Video Library, Inc.\'s search engine. My Video Library (herein MVL) provides its website services to you subject to the following conditions. If you visit My Video Library.com, use other MVL services or applications, you accept these conditions. Please read them carefully.Your use and access to the MVL website and your use of the services are strictly conditioned upon your confirmation that you comply fully with our terms and conditions of use. By accessing and using MyVideoLibrary.com or otherwise using this website, you signify your unequivocal acceptance of these and any other conditions and terms prevailing at this or at any future time.  You agree to adhere to the terms and conditions of use detailed herein without evasion, equivocation or reservation of any kind, in the knowledge that failure to comply with the terms and conditions will result in suspension or denial of your access to the website and potential legal and civil penalties.\nDefinitions\nThe term \'the website\' applies to the site (MyVideoLibrary.com), its staff, administration, owners, agents, representatives, suppliers and partners. The term \'the user\' applies to any website visitor who wishes to use the website once arriving at MyVideoLibrary.com.")
        plugin.log.info("clicked")
        curr_page = 1
    elif curr_page == 3:
        window.textbox.setText(
            "Relationship\nThe relationship between you (the user) and us (MVL) is that we provide you with access to the referencing material and media contained within our site, which is provided to you on a purely non commercial basis and is, therefore, not that of customer and supplier.\nContent\nOther than descriptive material about the movies, MVL does not host, provide, archive, store, or distribute media of any kind, and acts merely as an index (or directory) of media posted by other webmasters on the internet, which is completely outside of our control. In general, we cannot and do not attempt to control, censor, or block any indexed material that may be considered offensive, abusive, libelous, obnoxious, inaccurate, deceptive, unlawful or otherwise distressing and neither do we accept responsibility for this content or the consequences of such content being made available.  Sometimes we do block referenced material because a third party asserts superior rights or for other legitimate reasons.  We are not responsible for your use of referenced material or your access to referenced material. ")
        plugin.log.info("clicked")
        curr_page = 2
    elif curr_page == 4:
        window.textbox.setText(
            "Material may be inappropriately described or subject to restrictions such as copyright, licensing and other limitations and it is the sole responsibility of those having access to such material to comply with any or all lawful obligations arising from such material coming into their possession and, thus mitigate any alleged transgression. All users warrant that they are 18 years of age or older, and, therefore, qualified to enter into this agreement either as an individual or as a corporate entity. All users undertake to comply with applicable laws and observe the rights inherent in any copyright material whilst upholding the rights of any copyright owner. All users are advised to use caution, discretion, common sense and personal judgment when using My Video Library.com or any references detailed within the directory and to respect the wishes of others who may value freedom, as consenting adults equal to (or possibly superior to) your own personal preferences.\nQuality Of Service\nMVL does not provide commercial services and there are no actual or implied guarantees as to the availability of service or the speed, operation or function of this website, which is offered on a basis to those who choose to comply with the terms and conditions detailed within and access the \'free\' content of this website.")
        plugin.log.info("clicked")
        curr_page = 3
    elif curr_page == 5:
        window.textbox.setText(
            "SOME JURISDICTIONS PROVIDE FOR CERTAIN WARRANTIES, LIKE THE IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. TO THE EXTENT PERMITTED BY LAW, WE EXCLUDE ALL WARRANTIES. \nIndemnification.\nYou, as a user of the website, agree to indemnify, defend, and hold MVL harmless from any and all liability, claims, actions, expenses (including attorneys\' fees and costs) that MVL may have relating to or arising from (a) your use of (or consequences of your use of) the website, or (b) any allegation that your use of the referenced material violates the trademark, copyright or other intellectual property rights of any third party.\nPrivacy\nThis website will comply with the requirements of any law enforcement or other officials, courts, or others with a legitimate interest in the official investigation or enforcement of applicable law.\nThe protection of the rights of others is important to MVL, and this extends to your adherence to intellectual property law, the rights of others to enjoy freedom from slander, libel, defamation, provocation, harassment, discrimination of any kind or any other action that may be deemed offensive by the individual concerned.")
        plugin.log.info("clicked")
        curr_page = 4
    elif curr_page == 6:
        window.textbox.setText(
            "MVL is committed to protecting your privacy. MVL does not sell, trade or rent your personal information to any other companies. MVL will not collect any personal information about you except when you specifically and knowingly provide such information when registering for the website.\nBy using our website, you consent to the collection and use of this information by MVL. If we decide to change our privacy policy, we will post any changes to this page so that you are aware of which information we collect, how we use it, and under which circumstances we disclose it.\nIntellectual Property - General\nMVL respects the rights of others, and prohibits the use of referenced material for any purpose other than that for which it is intended (where such use is lawful and free of civil liability or other constraint) and in such circumstances where possession of such material may have any adverse financial, prejudicial or any other effect on any other third party.\nIf you believe in good faith your work has been copied in a way that constitutes copyright infringement, or that your intellectual property rights have been otherwise violated, please provide the following to MVL\'s Copyright Agent:\nA description of the copyrighted work or intellectual property that you claim has been infringed, or if multiple works, a listing of such works.")
        plugin.log.info("clicked")
        curr_page = 5


def check_condition():
    macAddress = usrsettings.getSetting('mac_address')
    global curr_page
    curr_page = 1
    url = server_url + "/api/index.php/api/authentication_api/get_flag_status?username={0}&mac={1}".format(username,
                                                                                                           macAddress)
    req = urllib2.Request(url)
    opener = urllib2.build_opener()
    # f = opener.open(req)
    #reading content fetched from the url
    # content = f.read()
    content = 'true'
    #converting to json object
    plugin.log.info(url)
    plugin.log.info(content)
    if content == 'false':
        global window
        window = AddonDialogWindow('Terms and Conditions')
        # Set the window width, height and the grid resolution: 2 rows, 3 columns.
        window.setGeometry(700, 500, 10, 10)

        # TextBox
        window.textbox = TextBox()
        window.placeControl(window.textbox, 0, 0, 9, 10)
        window.textbox.setText(
            "General\nWelcome to My Video Library, Inc.\'s search engine. My Video Library (herein MVL) provides its website services to you subject to the following conditions. If you visit My Video Library.com, use other MVL services or applications, you accept these conditions. Please read them carefully.Your use and access to the MVL website and your use of the services are strictly conditioned upon your confirmation that you comply fully with our terms and conditions of use. By accessing and using MyVideoLibrary.com or otherwise using this website, you signify your unequivocal acceptance of these and any other conditions and terms prevailing at this or at any future time.  You agree to adhere to the terms and conditions of use detailed herein without evasion, equivocation or reservation of any kind, in the knowledge that failure to comply with the terms and conditions will result in suspension or denial of your access to the website and potential legal and civil penalties.\nDefinitions\nThe term \'the website\' applies to the site (MyVideoLibrary.com), its staff, administration, owners, agents, representatives, suppliers and partners. The term \'the user\' applies to any website visitor who wishes to use the website once arriving at MyVideoLibrary.com.")

        # window.textbox.setText('General\nWelcome to My V')
        # Create a button.
        next = Button('Next')
        # Place the label on the window grid.
        window.placeControl(next, 9, 8, columnspan=2)
        window.connect(next, next_page)

        prev = Button('Previous')
        # Place the label on the window grid.
        window.placeControl(prev, 9, 0, columnspan=2)
        window.connect(prev, prev_page)

        # Create a button.
        button = Button('I Agree')
        button2 = Button('Do Not Agree')

        # Place the button on the window grid.
        window.placeControl(button, 9, 3, columnspan=2)
        window.placeControl(button2, 9, 5, columnspan=2)

        # Set initial focus on the button.
        window.setFocus(button)
        # Connect the button to a function.
        window.connect(button, onClick_agree)
        window.connect(button2, onClick_disAgree)
        # Show the created window.
        window.doModal()
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
        xbmc.executebuiltin(
            'Notification(Mac Address Not Available,MVL Could not get the MAC Address,5000,/script.hellow.world.png)')

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
    global internet_info
    internet_info = AddonDialogWindow('INTERNET CONNECTION ISSUE')
    # Set the window width, height and the grid resolution: 2 rows, 3 columns.
    internet_info.setGeometry(450, 200, 6, 6)

    # TextBox
    internet_info.textbox = TextBox()
    internet_info.placeControl(internet_info.textbox, 0, 0, 5, 6)
    internet_info.textbox.setText(
        "An error has occured communicating with MyVideoLibrary server. Please check that you are connected to internet through wi-fi")

    # Create a button.
    okay = Button('OK')

    # Place the label on the window grid.
    internet_info.placeControl(okay, 4, 2, columnspan=2, rowspan=2)
    internet_info.setFocus(okay)
    internet_info.connect(okay, show_root)
    # Show the created window.
    internet_info.doModal()


def show_root():
    global internet_info
    internet_info.close()
    sys_exit()


@plugin.route('/categories/<id>/<page>')
def get_categories(id, page):
    #import resources.htmlcleaner
    #import re

    if check_internet():
        global mvl_view_mode
        global mvl_tvshow_title
        try:

            dp = xbmcgui.DialogProgress()
            
            if id in ('23', '32'): # if the Parent ID is Genres for TV or Movies then view should be set as "List" mode
                mvl_view_mode = 50
            elif id in ('1', '3'):  # if these are immediate childs of Top Level parents then view should be set as Fan Art
                mvl_view_mode = 59
                # else:
                # mvl_view_mode = 59

            parent_id = id
            main_category_check = False
            is_search_category = False
            top_level_parent = 0
            xbmcplugin.setContent(pluginhandle, 'Movies')
            plugin.log.info(id)
            plugin.log.info(page)
            plugin.log.info(page_limit)
            
            url = server_url + "/api/index.php/api/categories_api/getCategories?parent_id={0}&page={1}&limit={2}".format(id,
                                                                                                                         page,
                                                                                                                         page_limit)
            plugin.log.info(url)
            req = urllib2.Request(url)
            opener = urllib2.build_opener()
            f = opener.open(req)
            content = f.read()
            items = []
            
            if content:
                jsonObj = json.loads(content)
                totalCats = len(jsonObj)
                plugin.log.info('total categories-->%s' % totalCats)
                plugin.log.info(jsonObj)
                if jsonObj[0]['top_level_parent'] == jsonObj[0]['parent_id']:
                    is_search_category = True

                item_count = len(jsonObj)
                done_count = 0
                dp_created = False
                dp_type = 'show'

                for categories in jsonObj:

                    try:    # The last item of Json only contains the one element in array with key as "ID" so causing the issue

                        plugin.log.info('{0}'.format(categories['is_playable']))
                        if categories['top_level_parent'] == categories['parent_id']:
                            main_category_check = True

                    except:
                        pass

                    if is_search_category == True:
                        is_search_category = False
                        #adding search option
                        items += [{
                                  'label': 'Search',
                                  'path': plugin.url_for('search', category=parent_id),
                                  'thumbnail': art('search.png'),
                                  'is_playable': False,
                                  }]

                    #categories['id'] is -1 when more categories are present and next page option should be displayed
                    if categories['id'] == -1:
                        items += [{
                                      'label': 'Next >>',
                                      'path': plugin.url_for('get_categories', id=parent_id, page=(int(page) + 1)),
                                      'is_playable': False,
                                      'thumbnail': art('next.png')
                                  }]
                    #categories['is_playable'] is False for all categories and True for all video Items
                    elif categories['is_playable'] == 'False':

                        if categories['top_level_parent'] == '3' and categories['parent_id'] not in (
                        '32', '3'):  # Parsing the TV Shows Titles & Seasons only
                            tmpTitle = categories['title'].encode('utf-8')

                            mvl_meta = ''
                            if tmpTitle == "Season 1":
                                tmpSeasons = []
                                mvl_view_mode = 50
                                # for i in range(totalCats):
                                # tmpSeasons.append( i )
                                #plugin.log.info('season found')
                                #mvl_meta = __metaget__.get_seasons(mvl_tvshow_title, '', tmpSeasons)
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

                            items += [{
                                          'label': '{0}'.format(categories['title']),
                                          'path': plugin.url_for('get_categories', id=categories['id'], page=0),
                                          'is_playable': False,
                                          'thumbnail': thumbnail_url,
                                          'properties': {
                                              'fanart_image': fanart_url,
                                          },
                                          'context_menu': [(
                                                               'Add to Favourites',
                                                               'XBMC.RunPlugin(%s)' % plugin.url_for('save_favourite',
                                                                                                     id=categories['id'],
                                                                                                     title=categories[
                                                                                                         'title'],
                                                                                                     thumbnail="None",
                                                                                                     isplayable="False",
                                                                                                     category=categories[
                                                                                                         'top_level_parent'])
                                                           )],
                                          'replace_context_menu': True
                                      }]

                        else:

                            items += [{
                                          'label': '{0}'.format(categories['title']),
                                          'path': plugin.url_for('get_categories', id=categories['id'], page=0),
                                          'is_playable': False,
                                          'thumbnail': art('{0}.png'.format(categories['title'].lower())),
                                          'context_menu': [(
                                                               'Add to Favourites',
                                                               'XBMC.RunPlugin(%s)' % plugin.url_for('save_favourite',
                                                                                                     id=categories['id'],
                                                                                                     title=categories[
                                                                                                         'title'],
                                                                                                     thumbnail="None",
                                                                                                     isplayable="False",
                                                                                                     category=categories[
                                                                                                         'top_level_parent'])
                                                           )],
                                          'replace_context_menu': True
                                      }]

                            #plugin.log.info(art('{0}.png'.format(categories['title'].lower())))

                    #inorder for the information to be displayed properly, corresponding labels should be added in skin
                    elif categories['is_playable'] == 'True':

                        if categories['source'] == '1':
                            thumbnail_url = categories['image_name']
                        else:
                            thumbnail_url = server_url + '/wp-content/themes/twentytwelve/images/{0}'.format(
                                categories['video_id'] + categories['image_name'])

                        mvl_img = thumbnail_url
                        mvl_meta = create_meta('movie', categories['title'].encode('utf-8'), categories['release_date'],
                                               mvl_img)
                        plugin.log.info('meta data-> %s' % mvl_meta)
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
                                          'cast': categories['actors'].encode('utf-8'),
                                          'year': categories['release_date']
                                      },
                                      'path': plugin.url_for('get_videos', id=categories['video_id'],
                                                             thumbnail=thumbnail_url),
                                      'is_playable': False,
                                      'context_menu': [(
                                                           'Add to Favourites',
                                                           'XBMC.RunPlugin(%s)' % plugin.url_for('save_favourite',
                                                                                                 id=categories['video_id'],
                                                                                                 title=categories[
                                                                                                     'title'].encode(
                                                                                                     'utf-8'),
                                                                                                 thumbnail=thumbnail_url,
                                                                                                 isplayable="True",
                                                                                                 category=categories[
                                                                                                     'top_level_parent'])
                                                       )],
                                      'replace_context_menu': True
                                  }]
                                  
                    if dp_created == False:
                        dp.create("Please wait while "+dp_type+" list is loaded","","")
                        dp_created = True
                                  
                    done_count = done_count + 1
                    dp.update((done_count*100/item_count), "This wont happen next time you visit.",  str(done_count)+" of "+str(item_count)+" "+dp_type+"s loaded so far.")

                    if dp.iscanceled():
                        break
                    
                                  

                if main_category_check == True:
                    #adding A-Z listing option
                    items += [{
                                  'label': 'A-Z Listings',
                                  'path': plugin.url_for('azlisting', category=parent_id),
                                  'thumbnail': art('A-Z.png'),
                                  'is_playable': False,
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
            
            return items
        except IOError:
            xbmc.executebuiltin('Notification(Unreachable Host,Could not connect to server,5000,/script.hellow.world.png)')
        except Exception, e:
            xbmc.executebuiltin('Notification(Unreachable Host,Could not connect to server,5000,/script.hellow.world.png)')
            plugin.log.info(e)
            traceback.print_exc()
    else:
        dialog_msg()


@plugin.route('/get_videos/<id>/<thumbnail>/')
def get_videos(id, thumbnail):
    if check_internet():
        global mvl_view_mode
        mvl_view_mode = 50
        try:
            url = server_url + "/api/index.php/api/categories_api/getVideoUrls?video_id={0}".format(id)
            req = urllib2.Request(url)
            opener = urllib2.build_opener()
            f = opener.open(req)
            content = f.read()
            jsonObj = json.loads(content)

            url = server_url + "/api/index.php/api/categories_api/getVideoTitle?video_id={0}".format(id)
            req = urllib2.Request(url)
            opener = urllib2.build_opener()
            f = opener.open(req)
            content = f.read()
            count = 0
            items = []
            plugin.log.info(jsonObj)

            for urls in jsonObj:
                count += 1
                items += [{
                              'label': '{0} Source {1}'.format(content, count),
                              'thumbnail': thumbnail,
                              'path': plugin.url_for('play_video', url=urls['URL']),
                              'is_playable': True,
                          }]

            return items
        except IOError:
            xbmc.executebuiltin('Notification(Unreachable Host,Could not connect to server,5000,/error.png)')
    else:
        dialog_msg()



@plugin.route('/play_video/<url>')
def play_video(url):
    if check_internet():
        global mvl_view_mode
        mvl_view_mode = 50
        #if login is successful then selected item will be resolved using urlresolver and played
        if login_check():
            hostedurl = urlresolver.HostedMediaFile(url).resolve()
            plugin.log.info(url)
            plugin.log.info(hostedurl)
            plugin.set_resolved_url(hostedurl)
        else:
            pass
    else:
        dialog_msg()

def create_meta(video_type, title, year, thumb):
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

        else:  # movie
            meta = __metaget__.get_meta(video_type, title, year=year)
            alt_id = meta['tmdb_id']

        if video_type == 'tvshow':
            meta['cover_url'] = meta['banner_url']
        if meta['cover_url'] in ('/images/noposter.jpg', ''):
            meta['cover_url'] = thumb
            
        print 'Done TV'
        print meta
        
    except Exception, e:
        plugin.log.info('Error assigning meta data for %s %s %s' % (video_type, title, year))
        plugin.log.info(e)
        traceback.print_exc()

    return meta


def login_check():
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
        plugin.log.info(myObj)

        #creating items from json object
        for row in myObj:
            if row['status'] == 1:
                return True
            else:
                xbmc.executebuiltin('Notification(License Limit Reached,' + row['message'] + ')')
                return False
    except IOError:
        xbmc.executebuiltin('Notification(Unreachable Host,Could not connect to server,5000,/error.png)')
    pass


@plugin.route('/search/<category>/')
def search(category):

    if check_internet():

        global mvl_view_mode
        
        try:

            search_string = plugin.keyboard(heading=('search'))
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
                xbmc.executebuiltin('Notification(Sorry,No Videos Found Matching Your Query,5000,/error.png)')
                mvl_view_mode = 59

            else:
                mvl_view_mode = 50
                jsonObj = json.loads(response)
                plugin.log.info(jsonObj)
                items = []
                item_count = len(jsonObj)
                done_count = 0
                dp_created = False
                dp_type = 'show'
                
                for categories in jsonObj:
                    if categories['is_playable'] == 'False':

                        items += [{
                                      'label': '{0}'.format(categories['title'].encode('utf-8')),
                                      'path': plugin.url_for('get_categories', id=categories['id'], page=0),
                                      'is_playable': False,
                                      'thumbnail': art('{0}.png'.format(categories['title'].lower())),
                                      'context_menu': [(
                                                           'Add to Favourites',
                                                           'XBMC.RunPlugin(%s)' % plugin.url_for('save_favourite',
                                                                                                 id=categories['id'],
                                                                                                 title=categories['title'],
                                                                                                 thumbnail="None",
                                                                                                 isplayable="False",
                                                                                                 category=category)
                                                       )],
                                      'replace_context_menu': True
                                  }]
                    elif categories['is_playable'] == 'True':
                        categories['title'] = categories['title'].encode('utf-8')
                        thumbnail_url = categories['thumbnail']

                        dp_type = 'movie'
                        
                        mvl_img = thumbnail_url
                        mvl_meta = create_meta('movie', categories['title'], '', thumbnail_url)
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

                        items += [{
                                      'label': '{0}'.format(categories['title']),
                                      'path': plugin.url_for('get_videos', id=categories['video_id'], thumbnail="None"),
                                      'is_playable': False,
                                      'thumbnail': thumbnail_url,
                                      'properties': {
                                          'fanart_image': fanart_url,
                                      },
                                      'context_menu': [(
                                                           'Add to Favourites',
                                                           'XBMC.RunPlugin(%s)' % plugin.url_for('save_favourite',
                                                                                                 id=categories['id'],
                                                                                                 title=categories['title'],
                                                                                                 thumbnail="None",
                                                                                                 isplayable="True",
                                                                                                 category=category)
                                                       )],
                                      'replace_context_menu': True
                                  }]
                                  
                    if dp_created == False:
                        dp.create("Please wait while "+dp_type+" list is loaded","","")
                        dp_created = True
                              
                    done_count = done_count + 1
                    dp.update((done_count*100/item_count), "This wont happen next time you visit.",  str(done_count)+" of "+str(item_count)+" "+dp_type+"s loaded so far.")

                    if dp.iscanceled():
                        break                                 
                        
                dp.close()
                
                return items
        except IOError:
            xbmc.executebuiltin('Notification(Unreachable Host,Could not connect to server,5000,/script.hellow.world.png)')
    else:
        dialog_msg()




@plugin.route('/azlisting/<category>/')
def azlisting(category):
    if check_internet():
        global mvl_view_mode
        mvl_view_mode = 50
        Indices = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                   'V', 'W', 'X', 'Y', 'Z']
        items = [{
                     'label': '#',
                     'thumbnail': art('#.png'),
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
        return items
    else:
        dialog_msg()


@plugin.route('/get_azlist/<key>/<page>/<category>/')
def get_azlist(key, page, category):
    global mvl_view_mode
    mvl_view_mode = 50
    page_limit_az = 50
    try:

        dp = xbmcgui.DialogProgress()
    
        url = server_url + "/api/index.php/api/categories_api/getAZList?key={0}&limit={1}&page={2}&category={3}".format(
            key, page_limit_az, page, category)
        plugin.log.info("here is the url")
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
                                  'path': plugin.url_for('get_azlist', key=key, page=(int(page) + 1),
                                                         category=category),
                                  'thumbnail': art('next.png'),
                                  'is_playable': False,
                              }]
                elif results['is_playable'] == 'False':
                    if results['parent_id'] not in ('32', '23'):  # if not Genres then show them
                        if results['top_level_parent'] == '3':      # if TV Series fetch there fan art
                            tmpTitle = results['title'].encode('utf-8')

                            mvl_meta = ''
                            if tmpTitle == "Season 1":
                                tmpSeasons = []
                                mvl_view_mode = 50
                                # for i in range(totalCats):
                                # tmpSeasons.append( i )
                                #plugin.log.info('season found')
                                #mvl_meta = __metaget__.get_seasons(mvl_tvshow_title, '', tmpSeasons)
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

                            items += [{
                                          'label': '{0}'.format(results['title'].encode('utf-8')),
                                          'path': plugin.url_for('get_categories', id=results['id'], page=0),
                                          'is_playable': False,
                                          'thumbnail': thumbnail_url,
                                          'properties': {
                                              'fanart_image': fanart_url,
                                          },
                                          'context_menu': [(
                                                               'Add to Favourites',
                                                               'XBMC.RunPlugin(%s)' % plugin.url_for('save_favourite',
                                                                                                     id=results['id'],
                                                                                                     title=results[
                                                                                                         'title'].encode(
                                                                                                         'utf-8'),
                                                                                                     thumbnail="None",
                                                                                                     isplayable="False",
                                                                                                     category=results[
                                                                                                         'top_level_parent'])
                                                           )],
                                          'replace_context_menu': True
                                      }]

                        else:
                            items += [{
                                          'label': '{0}'.format(results['title'].encode('utf-8')),
                                          'path': plugin.url_for('get_categories', id=results['id'], page=0),
                                          'is_playable': False,
                                          'thumbnail': art('{0}.png'.format(results['title'].lower())),
                                          'context_menu': [(
                                                               'Add to Favourites',
                                                               'XBMC.RunPlugin(%s)' % plugin.url_for('save_favourite',
                                                                                                     id=results['id'],
                                                                                                     title=results[
                                                                                                         'title'].encode(
                                                                                                         'utf-8'),
                                                                                                     thumbnail="None",
                                                                                                     isplayable="False",
                                                                                                     category=category)
                                                           )],
                                          'replace_context_menu': True
                                      }]

                elif results['is_playable'] == 'True':
                    results['title'] = results['title'].encode('utf-8')
                    thumbnail_url = results['thumbnail']
                    
                    dp_type = 'movie'

                    mvl_img = thumbnail_url
                    mvl_meta = create_meta('movie', results['title'].encode('utf-8'), '', thumbnail_url)
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
                                  'label': '{0}'.format(results['title'].encode('utf-8')),
                                  'path': plugin.url_for('get_videos', id=results['video_id'],
                                                         thumbnail=results['thumbnail']),
                                  'thumbnail': thumbnail_url,
                                  'properties': {
                                      'fanart_image': fanart_url,
                                  },
                                  'is_playable': False,
                                  'context_menu': [(
                                                       'Add to Favourites',
                                                       'XBMC.RunPlugin(%s)' % plugin.url_for('save_favourite',
                                                                                             id=results['video_id'],
                                                                                             title=results[
                                                                                                 'title'].encode(
                                                                                                 'utf-8'),
                                                                                             thumbnail="None",
                                                                                             isplayable="True",
                                                                                             category=category)
                                                   )],
                                  'replace_context_menu': True
                              }]

                if dp_created == False:
                    dp.create("Please wait while "+dp_type+" list is loaded","","")
                    dp_created = True
                              
                done_count = done_count + 1
                dp.update((done_count*100/item_count), "This wont happen next time you visit.",  str(done_count)+" of "+str(item_count)+" "+dp_type+"s loaded so far.")

                if dp.iscanceled():
                    break
                
            plugin.log.info('itemcheck')
            plugin.log.info(items)
            
            dp.close()
            
            return items
        else:
            xbmc.executebuiltin('Notification(Sorry,No Videos Available In this Category,5000,/error.png)')
    except IOError:
        xbmc.executebuiltin('Notification(Unreachable Host,Could not connect to server,5000,/script.hellow.world.png)')


@plugin.route('/mostpopular/<page>/<category>/')
def mostpopular(page, category):
    global mvl_view_mode
    mvl_view_mode = 50
    try:

        dp = xbmcgui.DialogProgress()
    
        url = server_url + "/api/index.php/api/categories_api/getMostPopular?limit={0}&page={1}&category={2}".format(
            page_limit, page, category)
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
                                  'path': plugin.url_for('get_videos', id=results['id'], thumbnail=thumbnail_url),
                                  'is_playable': False,
                                  'context_menu': [(
                                                       'Add to Favourites',
                                                       'XBMC.RunPlugin(%s)' % plugin.url_for('save_favourite',
                                                                                             id=results['id'],
                                                                                             title=results['title'],
                                                                                             thumbnail=thumbnail_url,
                                                                                             isplayable="True",
                                                                                             category=category)
                                                   )],
                                  'replace_context_menu': True
                              }]

                if dp_created == False:
                    dp.create("Please wait while "+dp_type+" list is loaded","","")
                    dp_created = True
                              
                done_count = done_count + 1
                dp.update((done_count*100/item_count), "This wont happen next time you visit.",  str(done_count)+" of "+str(item_count)+" "+dp_type+"s loaded so far.")

                if dp.iscanceled():
                    break
            
            dp.close()
            
            return items
        else:
            xbmc.executebuiltin('Notification(Sorry,No Videos Available In this Category,5000,/error.png)')
    except IOError:
        xbmc.executebuiltin('Notification(Unreachable Host,Could not connect to server,5000,/script.hellow.world.png)')


def init_database():
    plugin.log.info('Building My Video Library Database')
    if not xbmcvfs.exists(os.path.dirname(DB_DIR)):
        xbmcvfs.mkdirs(os.path.dirname(DB_DIR))
    db = orm.connect(DB_DIR)
    db.execute(
        'CREATE TABLE IF NOT EXISTS favourites (id, title, thumbnail, isplayable, category, PRIMARY KEY (id, title, category))')
    db.commit()
    db.close()


@plugin.route('/save_favourite/<id>/<title>/<thumbnail>/<isplayable>/<category>')
def save_favourite(id, title, thumbnail, isplayable, category):
    plugin.log.info(id)
    plugin.log.info(title)
    plugin.log.info(thumbnail)
    plugin.log.info(isplayable)
    plugin.log.info(category)
    try:
        statement = 'INSERT OR IGNORE INTO favourites (id, title, thumbnail, isplayable, category) VALUES (%s,%s,%s,%s,%s)'
        db = orm.connect(DB_DIR)
        statement = statement.replace("%s", "?")
        cursor = db.cursor()
        cursor.execute(statement, (id, title, thumbnail, isplayable, category))
        db.commit()
        db.close()
    except:
        xbmc.executebuiltin(
            'Notification(Database Error,Please contact software provider,5000,/script.hellow.world.png)')


@plugin.route('/remove_favourite/<id>/<title>/<category>')
def remove_favourite(id, title, category):
    statement = 'DELETE FROM favourites WHERE id=%s AND title=%s AND category=%s'
    db = orm.connect(DB_DIR)
    statement = statement.replace("%s", "?")
    cursor = db.cursor()
    cursor.execute(statement, (id, title, category))
    db.commit()
    db.close()
    return xbmc.executebuiltin("XBMC.Container.Refresh()")


def sys_exit():
    xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
    return exit


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
    return items


if __name__ == '__main__':
    plugin.run()
    xbmc.executebuiltin("Container.SetViewMode(%s)" % mvl_view_mode)
