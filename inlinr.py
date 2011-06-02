from lxml.html import parse, tostring
import re
from urlparse import urlparse, urljoin
import urllib

def readurl(link, baseurl=None):
	if baseurl:
		link = urljoin(baseurl, link)
	return urllib.urlopen(link).read()

def inline_html(url):
	tree = parse(urllib.urlopen(url))

	for element, attribute, link, pos in tree.getroot().iterlinks():
		if element.tag == 'script':
			del element.attrib['src']
			element.text = readurl(link, url)
		elif element.tag == 'link' and element.attrib['rel']=='stylesheet':
			element.clear()
			element.tag = 'style'
			element.text = readurl(link, url)
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
