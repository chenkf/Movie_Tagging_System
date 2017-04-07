import urllib2
from bs4 import BeautifulSoup
import re

def tagFilter(tag):

	return (tag.name == "p") and (not tag.has_attr("class")) and (tag.contents[0].name != "b")


id = 'tt0111161'

keywordFile = open(id + " keyword", "w")


url = "http://www.imdb.com/title/" + id + "/keywords?ref_=tt_stry_kw"
response = urllib2.urlopen(url)
html = response.read()
soup = BeautifulSoup(html, 'html.parser')
keywords = soup.find_all(class_ = "sodatext")

print keywords

for keyword in keywords:

 	keywordFile.write(str(keyword.string) + " ")
 	print keyword