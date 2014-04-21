from base import BaseResolver
import re
import urllib2
import urllib
import logging
import unittest
import cgi
import sys

try:
    import simplejson as json
except ImportError:
    import json

logger = logging.getLogger('mvlresolver')

def decrypt_signature(self, s):
    ''' use decryption solution by Youtube-DL project '''
    if len(s) == 93:
        return s[86:29:-1] + s[88] + s[28:5:-1]
    elif len(s) == 92:
        return s[25] + s[3:25] + s[0] + s[26:42] + s[79] + s[43:79] + s[91] + s[80:83]
    elif len(s) == 91:
        return s[84:27:-1] + s[86] + s[26:5:-1]
    elif len(s) == 90:
        return s[25] + s[3:25] + s[2] + s[26:40] + s[77] + s[41:77] + s[89] + s[78:81]
    elif len(s) == 89:
        return s[84:78:-1] + s[87] + s[77:60:-1] + s[0] + s[59:3:-1]
    elif len(s) == 88:
        return s[7:28] + s[87] + s[29:45] + s[55] + s[46:55] + s[2] + s[56:87] + s[28]
    elif len(s) == 87:
        return s[6:27] + s[4] + s[28:39] + s[27] + s[40:59] + s[2] + s[60:]
    elif len(s) == 86:
        return s[5:34] + s[0] + s[35:38] + s[3] + s[39:45] + s[38] + s[46:53] + s[73] + s[54:73] + s[85] + s[74:85] + s[53]
    elif len(s) == 85:
        return s[3:11] + s[0] + s[12:55] + s[84] + s[56:84]
    elif len(s) == 84:
        return s[81:36:-1] + s[0] + s[35:2:-1]
    elif len(s) == 83:
        return s[81:64:-1] + s[82] + s[63:52:-1] + s[45] + s[51:45:-1] + s[1] + s[44:1:-1] + s[0]
    elif len(s) == 82:
        return s[80:73:-1] + s[81] + s[72:54:-1] + s[2] + s[53:43:-1] + s[0] + s[42:2:-1] + s[43] + s[1] + s[54]
    elif len(s) == 81:
        return s[56] + s[79:56:-1] + s[41] + s[55:41:-1] + s[80] + s[40:34:-1] + s[0] + s[33:29:-1] + s[34] + s[28:9:-1] + s[29] + s[8:0:-1] + s[9]
    elif len(s) == 80:
        return s[1:19] + s[0] + s[20:68] + s[19] + s[69:80]
    elif len(s) == 79:
        return s[54] + s[77:54:-1] + s[39] + s[53:39:-1] + s[78] + s[38:34:-1] + s[0] + s[33:29:-1] + s[34] + s[28:9:-1] + s[29] + s[8:0:-1] + s[9]
    else:
        logger.log(u'Unable to decrypt signature, key length %d not supported; retrying might work' % (len(s)))

def removeAdditionalEndingDelimiter(data):
    pos = data.find("};")
    if pos != -1:
        logger.info(u"found extra delimiter, removing")
        data = data[:pos + 1]
    return data

def extractFlashVars(data):
    flashvars = {}
    found = False

    for line in data.split("\n"):
        if line.strip().find(";ytplayer.config = ") > 0:
            found = True
            p1 = line.find(";ytplayer.config = ") + len(";ytplayer.config = ") - 1
            p2 = line.rfind(";")
            if p1 <= 0 or p2 <= 0:
                continue
            data = line[p1 + 1:p2]
            break
    data = removeAdditionalEndingDelimiter(data)

    if found:
        data = json.loads(data)
        flashvars = data["args"]

    return flashvars

def scrapeWebPageForVideoLinks(html):
    links = {}

    flashvars = extractFlashVars(html)
    if not flashvars.has_key(u"url_encoded_fmt_stream_map"):
        return links

    # if flashvars.has_key(u"ttsurl"):
    #     video[u"ttsurl"] = flashvars[u"ttsurl"]

    # if flashvars.has_key(u"hlsvp"):
    #     video[u"hlsvp"] = flashvars[u"hlsvp"]

    for url_desc in flashvars[u"url_encoded_fmt_stream_map"].split(u","):
        url_desc_map = cgi.parse_qs(url_desc)
        logger.info(u"url_map: " + repr(url_desc_map), 2)
        if not (url_desc_map.has_key(u"url") or url_desc_map.has_key(u"stream")):
            continue

        key = int(url_desc_map[u"itag"][0])
        url = u""
        if url_desc_map.has_key(u"url"):
            url = urllib.unquote(url_desc_map[u"url"][0])
        elif url_desc_map.has_key(u"conn") and url_desc_map.has_key(u"stream"):
            url = urllib.unquote(url_desc_map[u"conn"][0])
            if url.rfind("/") < len(url) -1:
                url = url + "/"
            url = url + urllib.unquote(url_desc_map[u"stream"][0])
        elif url_desc_map.has_key(u"stream") and not url_desc_map.has_key(u"conn"):
            url = urllib.unquote(url_desc_map[u"stream"][0])

        if url_desc_map.has_key(u"sig"):
            url = url + u"&signature=" + url_desc_map[u"sig"][0]
        elif url_desc_map.has_key(u"s"):
            sig = url_desc_map[u"s"][0]
            url = url + u"&signature=" + self.decrypt_signature(sig)

        links[key] = url

    return links


def selectVideoQuality(links):

    link = links.get
    video_url = ""

    hd_quality = 3

    # SD videos are default, but we go for the highest res
    if (link(35)):
        video_url = link(35)
    elif (link(59)):
        video_url = link(59)
    elif link(44):
        video_url = link(44)
    elif (link(78)):
        video_url = link(78)
    elif (link(34)):
        video_url = link(34)
    elif (link(43)):
        video_url = link(43)
    elif (link(26)):
        video_url = link(26)
    elif (link(18)):
        video_url = link(18)
    elif (link(33)):
        video_url = link(33)
    elif (link(5)):
        video_url = link(5)

    if hd_quality > 1: # <-- 720p
        if (link(22)):
            video_url = link(22)
        elif (link(45)):
            video_url = link(45)
        elif link(120):
            video_url = link(120)
    if hd_quality > 2:
        if (link(37)):
            video_url = link(37)
        elif link(121):
            video_url = link(121)

    if link(38) and False:
        video_url = link(38)

    if not len(video_url) > 0:
        return video_url

    # if video_url.find("rtmp") == -1:
    # 		video_url += '|' + urllib.urlencode({'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201'})

    return video_url

def parse_query(query, defaults={'mode': 'main'}):

        queries = cgi.parse_qs(query)
        q = defaults
        for key, value in queries.items():
            if len(value) == 1:
                q[key] = value[0]
            else:
                q[key] = value
        return q


class YouTubeResolver(BaseResolver):
    name = "youtube"

    def __init__(self):
        pass


    def get_media_url(self, host, media_id):
        try:
            response = urllib2.urlopen("https://www.youtube.com/watch?v=%s" % media_id)
            html = response.read()
            links = scrapeWebPageForVideoLinks(html)
            media_url = selectVideoQuality(links)
            if media_url == None:
                return None
            return media_url
        except Exception, e:
            logger.error("YouTube Error occured", exc_info=True)
            return None


    def get_url(self, host, media_id):
        return 'http://youtube.com/watch?v=%s' % media_id


    def get_host_and_id(self, url):

        if url.find('?') > -1:
            queries = parse_query(url.split('?')[1])
            video_id = queries.get('v', None)
        else:
            r = re.findall('/([0-9A-Za-z_\-]+)', url)
            if r:
                video_id = r[-1]

        if video_id:
          return (self.name, video_id)

        return None


    def valid_url(self, url, host):
        return re.match('http(s)?://(((www.)?youtube.+?(v|embed)(=|/))|' +
                        'youtu.be/)[0-9A-Za-z_\-]+',
                        url) != None


class YouTubeTest(unittest.TestCase):
    def setUp(self):
        self.obj = YouTubeResolver()


    def tearDown(self):
        self.obj = None


    def test_valid_url(self):
        self.assertEqual(self.obj.valid_url("http://youtube.com.bd/abcdef", "youtube"), False)
        self.assertEqual(self.obj.valid_url("https://www.youtube.com/watch?v=zCy5WQ9S4c0", "youtube"), True)


    def test_get_url(self):
        self.assertEqual(self.obj.get_url("youtube", "zCy5WQ9S4c0"), "http://youtube.com/watch?v=zCy5WQ9S4c0")


    def test_get_media_url(self):
        self.assertNotEqual(self.obj.get_media_url("youtube", "zCy5WQ9S4c0"), None) # Valid Link
        self.assertEqual(self.obj.get_media_url("youtube", "alalala"), None) # File Not Found


if __name__ == '__main__':
    unittest.main()
