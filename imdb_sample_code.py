import urllib2
from bs4 import BeautifulSoup
import re
import json
import pydot
import itertools
import time
import pydot

# step1
url = 'http://www.imdb.com/search/title?at=0&sort=num_votes&count=100'
response = urllib2.urlopen(url)
step1_html = response.read()

with open("step1.html", "w") as f:
    f.write(step1_html)


# step2

soup = BeautifulSoup(step1_html, 'html.parser')
#print soup.prettify()
a_tag=soup.find_all(href=re.compile("/title/[a-zA-Z0-9].+li_tt"))

title_list = list()
id_list= list()

for i in a_tag:
    title = i.contents[0].encode('utf-8')
    id = i.get('href').encode('utf-8')
    id = re.findall(r'/title/([a-zA-Z0-9]+)/',id)[0]
    title_list.append(title)
    id_list.append(id)

year_list = list()
span_tag = soup.find_all('span', "lister-item-year text-muted unbold")
for i in span_tag:
    year_list.append(i.get_text().encode('utf-8'))



with open("step2.txt", "w") as f:
    for i in range(100):
        f.write(id_list[i] + '\t' + str(i+1) + '\t' + title_list[i] + ' ' + year_list[i] + '\n')


# step3

omdb_list = list()
for i in range(100):
    imdb = urllib2.urlopen("http://www.omdbapi.com/?i=" + str(id_list[i]) + "&r=json")
    imdb_html = imdb.read()
    omdb_list.append(imdb_html)
    time.sleep(5)

with open("step3.txt", "w") as f:
    for i in range(100):
        f.write(omdb_list[i] + '\n')


# step4

movie_name = list()
actors = list()
with open("step3.txt", "r") as f:
    for line in f:
        decoded = json.loads(line)
        movie_name.append(decoded['Title'].encode('utf-8'))
        actors.append(decoded['Actors'].encode('utf-8').split(', '))

with open("step4.txt", "w") as f:
    for i in range(100):
        f.write(movie_name[i] + '\t' + json.dumps(actors[i]) + '\n')       


# step5

actors = list()
with open("step4.txt", "r") as f:
    for line in f:
        a = line.strip().split('\t')
        decoded = json.loads(a[1])
        actors.append(decoded)

graph = pydot.Dot(graph_type='graph', charset="utf8")
for i in range(100):
    edge_list = list(itertools.combinations(actors[i], 2))
    for j in range(len(edge_list)):
        edge = pydot.Edge(edge_list[j])
        graph.add_edge(edge)


graph.write("actors_graph_output.dot")




