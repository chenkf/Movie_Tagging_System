import urllib2
from bs4 import BeautifulSoup
import re
import io

titlesIdsFile = io.open("titles_ids.txt", "w", encoding='utf8')

url = "http://www.imdb.com/chart/top?ref_=nv_mv_250_6"
response = urllib2.urlopen(url)
html = response.read()
soup = BeautifulSoup(html, 'html.parser')
titles = soup.find_all(class_ = "titleColumn")
ids = soup.find_all(class_ = "wlb_ribbon")


for i in range(len(titles)):

 	titlesIdsFile.write(titles[i].a.string + "| " + ids[i]["data-tconst"] + "\n")