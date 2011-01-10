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
from urllib import urlencode
from urllib2 import HTTPError
from BeautifulSoup import BeautifulSoup as BS, SoupStrainer as SS
import re
import urlparse

MODE_YALE_DEPARTMENTS = '20'
MODE_YALE_COURSES = '21'
MODE_YALE_LECTURES = '22'
MODE_YALE_PLAYVIDEO = '23'
DEFAULT_MODE = MODE_YALE_DEPARTMENTS

class _BasePluginHandler(XBMCVideoPluginHandler):
    base_url = 'http://oyc.yale.edu'

    def urljoin(self, path):
        return urlparse.urljoin(self.base_url, path)

class Departments(_BasePluginHandler):
    '''Lists the Departments found on http://oyc.yale.edu/'''
    def run(self):
        src = urlread(self.base_url)
        dd_tags = BS(src, parseOnlyThese=SS('dd', {'class': 'portletItem'}))

        items = [{'name': tag.a['title'],
                  'url': tag.a['href'],
                  'mode': MODE_YALE_COURSES} for tag in dd_tags]

        self.app.add_dirs(items)

class Courses(_BasePluginHandler):
    '''Lists courses found on a department page.

    e.g. http://oyc.yale.edu/astronomy
    '''
    def run(self):
        src = urlread(self.args['url'])
        table_tag = BS(src, parseOnlyThese=SS('table', {'summary': 'courses'}))

        #can't parse trs, some of the pages are missing tr tags
        #so parse, imgs, courses separately and zip together
        imgs = table_tag.findAll('img')
        courses = table_tag.findAll('td', {'class': 'departmentRightColumn'})

        items = [{'name': course.strong.string,
                  'mode': MODE_YALE_LECTURES,
                  'url': self.urljoin(course.a['href']),
                  'info': {'title': course.strong.string,
                           'plot': course.findAll('p')[-1].contents[0],
                           'credits': course.a.contents[2],
                            },
                  'tn': self.urljoin(img['src'])
                  } for course, img in zip(courses, imgs)]

        self.app.add_dirs(items)

class Lectures(_BasePluginHandler):
    '''Lists lectures found on a course's downloads page.

    e.g. http://oyc.yale.edu/astronomy/frontiers-and-controversies-in-astrophysics/content/downloads
    '''
    def run(self):
        #Course's downloads pages don't follow a particular pattern,
        #so visit each course page, then parse the link to the Downloads page
        html = BS(urlread(self.args['url']))
        url = html.find('a', {'title': 'Downloads'})['href']
        src = urlread(url)
        table_tag = BS(src, parseOnlyThese=SS('table', {'id': 'downloadsTable'}))

        #filter out trs that don't contain a lecture such as header, footer rows
        lecture_tags = filter(lambda t: t.a, table_tag.findAll('tr'))

        items = [{'name': ''.join(tag.findAll('td')[1].findAll(text=True)).strip(),
                  'mode': MODE_YALE_PLAYVIDEO,
                  'url': tag.a['href'],
                  'referer': url,
                  } for tag in lecture_tags]

        self.app.add_resolvable_dirs(items)

class PlayVideo(_BasePluginHandler):
    '''Builds a video url by appending a referer header to the url
    
    e.g. http://openmedia.yale.edu/cgi-bin/open_yale/media_downloader.cgi?file=/courses/spring07/astr160/mov/astr160_01_011607.mov|referer=http://oyc.yale.edu/astronomy/frontiers-and-controversies-in-astrophysics/content/downloads
    '''
    def run(self):
        #The web server doesn't return the video stream unless an HTTP referer header is present.
        #To use in XBMC, append '|referer=http://www.host.com/referer/ul'
        #Protocol arguments are key=val, appended to the end of a url after a pipe, '|'.
        #Found info in trac ticket, http://trac.xbmc.org/ticket/8971
        self.app.set_resolved_url('%s|referer=%s' % (self.args['url'], self.args['referer']))

site_listing = {'name': 'Yale',
                'mode': DEFAULT_MODE, 
                'info': {'plot': 'Open Yale Courses provides free and open access to a selection of introductory courses taught by distinguished teachers and scholars at Yale University. The aim of the project is to expand access to educational materials for all who wish to learn.',
                        'title': 'Yale'},
} 

handler_map = [(MODE_YALE_DEPARTMENTS, Departments),
               (MODE_YALE_COURSES, Courses),
               (MODE_YALE_LECTURES, Lectures),
               (MODE_YALE_PLAYVIDEO, PlayVideo),
              ]

