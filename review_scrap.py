import urllib2
from bs4 import BeautifulSoup
import re

def tagFilter(tag):

	return (tag.name == "p") and (not tag.has_attr("class")) and (tag.contents[0].name != "b")

titlesIdsFile = open("titles_ids.txt")

for line in titlesIdsFile.readlines():

	id = line.split("| ")[1][:-1]

	pageIndex = 0

	reviewFile = open("reviews\\" + id, "w")

	proceed = True
	maxIndex = 1

	while proceed and pageIndex < maxIndex:

		url = 'http://www.imdb.com/title/' + id + '/reviews?start=' + str(pageIndex * 10)
		response = urllib2.urlopen(url)
		html = response.read()
		soup = BeautifulSoup(html, 'html.parser')
		reviewsSinglePage = soup.find_all(tagFilter)[1 : -2]

		reviews = []

		if reviewsSinglePage == []:

			proceed = False;

		else:

			reviews.extend(reviewsSinglePage)
			pageIndex += 1

		for review in reviews:

			reviewStr = re.sub(r"(\r)|(\n)", " ", str(review))
	 		reviewFile.write(re.sub(r"(<p>)|(</p>)|(<br>)|(</br>)|(\r)|(\n)", "", reviewStr) + "\n")