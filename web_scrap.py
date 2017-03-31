import urllib2
from bs4 import BeautifulSoup
import re
import json
import pydot
import itertools
import time

# step1
id = 'tt0111161'
num_page = 10
reviews = []
for page in range(num_page): 
    url = 'http://www.imdb.com/title/'+id+'/reviews?start='+str(num_page * 10)
    response = urllib2.urlopen(url)
    step1_html = response.read()
    soup = BeautifulSoup(step1_html, 'html.parser')
    reviews.append(soup.find_all(re.compile("^p"),attrs={'class': None})[1:-2])
    time.sleep(5)