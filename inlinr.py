#!/usr/bin/python

# inlinr - embed all linked resources into an HTML page
# (C) 2011 Kevin Mehall <km@kevinmehall.net>
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# usage: inlinr.py <url or filename> <destination file>

from lxml.html import parse, tostring
from urlparse import urljoin
import re
import base64
import urllib

def readurl(link, baseurl=None, binary=False):
	print link
	if baseurl:
		link = urljoin(baseurl, link)
	d = urllib.urlopen(link).read()
	if not binary:
		d = d.decode('utf8')
	return d
	
css_re = re.compile('''url\('(.+)'\)''')
def inline_css(link, parenturl):
	data = readurl(link, parenturl)
	
	def replace(match):
		d = readurl(match.group(1), parenturl, True) #TODO: use CSS basename
		return unicode("url('data:image/png;base64,"+base64.b64encode(d)+"')") #TODO: content-type
	
	return css_re.sub(replace, data)

def inline_html(url):
	"""
	Returns a version of the page at url/filename `url` with linked resources
	replaced by embeds
	"""
	tree = parse(urllib.urlopen(url))

	for element, attribute, link, pos in tree.getroot().iterlinks():
		if '://' in link:
			continue
		if element.tag == 'script':
			del element.attrib['src']
			element.text = readurl(link, url)
		elif element.tag == 'link' and element.attrib['rel']=='stylesheet':
			element.clear()
			element.tag = 'style'
			element.text = inline_css(link, url)
		elif element.tag == 'a':
			pass
		else:
			print "Warning: don't know how to handle link in %s: %s"%(element.tag, link)

	return tostring(tree, method='html')
	
if __name__ == '__main__':
	import sys
	
	if len(sys.argv) >= 2:
		infile = sys.argv[1]
	else:
		infile = 'index.html'
		
	if len(sys.argv) >= 3:
		outfile = sys.argv[2]
	else:
		outfile = infile.replace('.html', '.inline.html')
		
	open(outfile, 'wt').write(inline_html(infile))
