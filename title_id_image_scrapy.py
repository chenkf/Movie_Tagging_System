import urllib2
from bs4 import BeautifulSoup
import io
import re

titlesIdsFile = io.open("titles_ids_images.csv", "w", encoding='utf8')

url = "http://www.imdb.com/chart/top?ref_=nv_mv_250_6"
response = urllib2.urlopen(url)
html = response.read()
soup = BeautifulSoup(html, 'html.parser')
titles = soup.find_all(class_ = "titleColumn")
ids = soup.find_all(class_ = "wlb_ribbon")
images = soup.find_all(src = re.compile("https://images-na.ssl-images-amazon.com"))

for i in range(len(titles)):

 	titlesIdsFile.write(titles[i].a.string + "," + ids[i]["data-tconst"] + "," + images[i]["src"] + "\n")