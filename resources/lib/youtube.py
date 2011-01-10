#!/usr/bin/env python
import re
import urllib
#from urlparse import parse_qs
from xbmccommon import parse_qs
from BeautifulSoup import BeautifulSoup as BS, SoupStrainer as SS

def get_flvs(videoid=None, url=None):
    #if videoid, construct url
    if videoid:
        url = 'http://www.youtube.com/watch?v=%s' % videoid
    src = urllib.urlopen(url).read()

    p = r'<param name=\\"flashvars\\" value=\\"(.+?)\\"'
    m = re.search(p, src)
    if not m:
        print 'error with match'
        return
    
    flashvars = m.group(1)
    params = parse_qs(flashvars)
    #when using urlparse.parse_qs, a list si returned for vals, so get 0th element
    #urls = params['fmt_url_map'][0].split(',')
    #fmts = params['fmt_list'][0].split(',')
    urls = params['fmt_url_map'].split(',')
    fmts = params['fmt_list'].split(',')


    urldict = dict((pair.split('|', 1) for pair in urls))
    fmtdict = dict((pair.split('/')[:2] for pair in fmts))
    flvs = dict(((fmtdict[key], urldict[key]) for key in urldict.keys()))
    return flvs





if __name__ == '__main__':
    #get_flvs('HoGsJgS7DWI')
    print get_flvs("2cFtUc7VdDs")

