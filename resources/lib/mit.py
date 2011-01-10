#!/usr/bin/env python
# Copyright 2011 Jonathan Beluch. 
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from xbmcvideoplugin import XBMCVideoPlugin, XBMCVideoPluginHandler
from xbmccommon import (urlread, async_urlread, DialogProgress, 
    parse_url_qs, XBMCVideoPluginException)
from youtube import get_flvs
from urllib import urlencode
from BeautifulSoup import BeautifulSoup as BS, SoupStrainer as SS
import re
import urlparse

#MODE_MIT_DEPARTMENTS = '10'
MODE_MIT_COURSES = '11'
MODE_MIT_LECTURES = '12'
MODE_MIT_VIDEO = '13'
DEFAULT_MODE = MODE_MIT_COURSES

class _BasePluginHandler(XBMCVideoPluginHandler):
    base_url = 'http://ocw.mit.edu'
    courses_url = 'http://ocw.mit.edu/courses/audio-video-courses/'

    def urljoin(self, path):
        return urlparse.urljoin(self.base_url, path)

class Courses(_BasePluginHandler):
    def run(self):
        src = urlread(self.courses_url)
        div_tags = BS(src, parseOnlyThese=SS('tr', {'class': re.compile('row|alt-row')}))

        #filter out classes that don't have full video lectures available
        video_divs = filter(lambda d: d.find('a', {'title': 'Video lectures'}), div_tags)

        items = [{'name': div.u.string,
                 'url': self.urljoin(div.a['href']),
                 'mode': MODE_MIT_LECTURES} for div in video_divs]
        self.app.add_dirs(items)

class Lectures(_BasePluginHandler):
    def parse_normal_course(self, div_tags):
        return [{'name': div.a['alt'].encode('utf-8'),
                  'url': self.urljoin(div.a['href']),
                  'tn': self.urljoin(div.img['src']),
                  'mode': MODE_MIT_VIDEO,
                  'info': {'title': div.a['alt'].encode('utf-8')},
                  } for div in div_tags]

    def parse_rm_course(self, src):
        #not implemented yet
        #example url: http://ocw.mit.edu/courses/urban-studies-and-planning/11-969-workshop-on-deliberative-democracy-and-dispute-resolution-summer-2005/lecture-notes/
        return [{'name': 'NO LECTURES FOUND'}]
        pass

    def run(self):
        src = urlread(self.args['url'])
        div_tags = BS(src, parseOnlyThese=SS('div', {'class': 'medialisting'}))

        #attempt to parse normal page
        if len(div_tags) > 0:
            items = self.parse_normal_course(div_tags)
        else:
            items = self.parse_rm_course(src)


        self.app.add_resolvable_dirs(items)

class PlayVideo(_BasePluginHandler):
    def get_high_quality(self, youtube_urls):
        hres = [(key, int(key.split('x')[0])) for key in youtube_urls.keys()]
        #highest quality is last in list
        hres = sorted(hres, key=lambda h: h[1])
        return youtube_urls[hres[-1][0]]
        
    def run(self):
        src = urlread(self.args['url'])
        p = r"http://www.youtube.com/v/(?P<videoid>.+?)'"
        m = re.search(p, src)
        if not m:
            print 'NO VIDEO FOUND'
            return
        youtube_urls = get_flvs(videoid=m.group('videoid'))
        url = self.get_high_quality(youtube_urls)
        #get highest quality by default for now
        #{'320x480': 'url', '480x720': 'url'}
        #self.app.set_resolved_url(youtube_urls.values()[0])
        self.app.set_resolved_url(url)


site_listing = {'name': 'MIT',
                'mode': DEFAULT_MODE, 
                'info': {'plot': 'Free lecture notes, exams, and videos from MIT.',
                        'title': 'MIT'},
} 

handler_map = [(MODE_MIT_COURSES, Courses),
               (MODE_MIT_LECTURES, Lectures),
               (MODE_MIT_VIDEO, PlayVideo),
              ]

