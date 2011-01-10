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
from BeautifulSoup import BeautifulSoup as BS, SoupStrainer as SS
import re
import urlparse

MODE_MITWORLD_TOPICS = '30'
MODE_MITWORLD_VIDEOS = '31'
MODE_MITWORLD_PLAYVIDEO = '32'
DEFAULT_MODE = MODE_MITWORLD_TOPICS

class _BasePluginHandler(XBMCVideoPluginHandler):
    base_url = 'http://mitworld.mit.edu'
    browse_url = 'http://mitworld.mit.edu/browse'
    topic_page_url = 'http://mitworld.mit.edu/browse/topic/%s/page:%s'

    def urljoin(self, path):
        return urlparse.urljoin(self.base_url, path)

    def pageurl(self, topic, page):
        return self.topic_page_url % (topic, page)

class Topics(_BasePluginHandler):
    def run(self):
        html = BS(urlread(self.browse_url))
        ul_tags = html.findAll('ul', {'class': 'links'})

        items = [{'name': a.string,
                  'url': self.urljoin(a['href']),
                  'topic': a['href'].rsplit('/', 1)[1],
                  'mode': MODE_MITWORLD_VIDEOS} for a in ul_tags[2].findAll('a')]
        self.app.add_dirs(items)


class Videos(_BasePluginHandler):
    def get_pagination_items(self, html, topic, page):
        items = []

        #if on page 2 or more, add an up listing to go back to topics
        #this way user doesn't have to click previous or '..' multiple times
        if int(page) > 1:
            items.append({'name': '^ List Topics',
                          'mode': MODE_MITWORLD_TOPICS})

        #check for presence of previous button
        a_prev = html.find('a', {'class': 'btn previous'})
        if a_prev:
            items.append({'name': '< Previous Videos',
                          'mode': MODE_MITWORLD_VIDEOS,
                          'topic': self.args['topic'],
                          'page': a_prev['href'].rsplit(':', 1)[1],
                          })

        #check for presence of next button
        a_next = html.find('a', {'class': 'btn next'})
        if a_next:
            items.append({'name': '> Next Videos',
                          'mode': MODE_MITWORLD_VIDEOS,
                          'topic': self.args['topic'],
                          'page': a_next['href'].rsplit(':', 1)[1],
                          })
        return items
            
    def run(self):
        page = self.args.get('page', 1)
        topic = self.args['topic']
        url = self.pageurl(topic, page)
        html = BS(urlread(url))

        items = [{'name': ''.join(tag.h4.a.findAll(text=True)).encode('utf-8'),
                  'url': self.urljoin(tag.a['href']),
                  'mode': MODE_MITWORLD_PLAYVIDEO,
                  'tn': self.urljoin(tag.img['src']),
                  'info': {'title': ''.join(tag.h4.a.findAll(text=True)).encode('utf-8'),
                           'aired': ''.join(tag.find('p', {'class': 'date'}).findAll(text=True)),
                           'credits': unicode(tag.find('p', {'class': 'speaker'}).string),
                           },
                    } for tag in html.findAll('li', {'class': 'video'})]

        pagination_items = self.get_pagination_items(html, topic, page)
        if len(pagination_items) > 0:
            self.app.add_dirs(pagination_items, end=False)

        self.app.add_resolvable_dirs(items)

class PlayVideo(_BasePluginHandler):
    def run(self):
        html = BS(urlread(self.args['url']))
        flashvars = html.find('embed')['src']
        params = parse_url_qs(flashvars)
        host = params['host']
        playpath = 'ampsflash/%s' % params['flv']
        url = 'rtmp://%s/ondemand?_fcs_vhost=%s' % (host, host)
        properties = {'PlayPath': playpath,
                      'TcUrl': url}

        self.app.play_video(url, info=self.args['info'], properties=properties)


site_listing = {'name': 'MIT World',
                'mode': DEFAULT_MODE, 
                'info': {'plot': "MIT World is a free and open site that provides on demand video of significant public events at MIT. MIT World's video index contains more than 700 videos.",
                        'title': 'MIT World'},
} 

handler_map = [(MODE_MITWORLD_TOPICS, Topics),
               (MODE_MITWORLD_VIDEOS, Videos),
               (MODE_MITWORLD_PLAYVIDEO, PlayVideo),
              ]

