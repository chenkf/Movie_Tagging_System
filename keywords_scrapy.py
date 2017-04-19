import urllib2
from bs4 import BeautifulSoup


titlesIdsFile = open("titles_ids.txt")

keywordsFile = open("keywords.txt", "w")

for line in titlesIdsFile.readlines():

	id = line.split("| ")[1][:-1]

	url = "http://www.imdb.com/title/" + id + "/keywords?ref_=tt_stry_kw"
	response = urllib2.urlopen(url)
	html = response.read()
	soup = BeautifulSoup(html, 'html.parser')
	keywordsBlocks = soup.find_all(class_ = "sodatext")

	keywords = []
	for keywordBlock in keywordsBlocks:

		keywords.append(str(keywordBlock.a.string))

	keywordsFile.write(", ".join(keywords) + "\n")