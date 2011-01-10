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
'''
DEFCON XBMC Addon

Watch presentations from past DEFCONs found at http://www.defcon.org

author:         Jonathan Beluch
project url:    https://github.com/jbeluch/xbmc-defcon
git url:        git://github.com/jbeluch/xbmc-defcon.git
version:        

Please report any issues at https://github.com/jbeluch/xbmc-defcon/issues
'''

from resources.lib.xbmcvideoplugin import XBMCVideoPlugin, XBMCVideoPluginHandler
from resources.lib.xbmccommon import (urlread, async_urlread, DialogProgress, 
    parse_url_qs, parse_qs, XBMCVideoPluginException, htmlentitydecode)
from urllib import urlencode
from BeautifulSoup import BeautifulSoup as BS, SoupStrainer as SS, BeautifulStoneSoup as BSS, NavigableString
import re
import urlparse
from htmlentitydefs import name2codepoint

#import sites
from resources.lib import mit
from resources.lib import yale
from resources.lib import mitworld

AVAILABLE_SITES = [mit, yale, mitworld]
PLUGIN_NAME = 'Open Courseware'
PLUGIN_ID = 'plugin.video.opencourseware'


MODE_SITES = '0'

class Sites(XBMCVideoPluginHandler):
    def run(self):
        items = [site.site_listing for site in AVAILABLE_SITES]
        app.add_dirs(items)


if __name__ == '__main__':
    settings = {'default_handler': Sites,
                'plugin_id': PLUGIN_ID, 
                'plugin_name': PLUGIN_NAME}

    app = XBMCVideoPlugin(
        [(MODE_SITES, Sites),] 
        + mit.handler_map 
        + yale.handler_map
        + mitworld.handler_map,
         **settings
    )
    app.run()
