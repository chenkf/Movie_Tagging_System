from flask import *
import csv

#from datetime import datetime
#from collections import namedtuple

main = Blueprint('main', __name__, template_folder='template')

@main.route('/', methods=['GET', 'PUT', 'POST'])
def main_route():

	keyphrases = []
	movie_ids = []
	with open('inverseIndex.csv','r') as f:
		reader = csv.reader(f, delimiter='|')
		for keyphrase, movie_id in reader:
			keyphrase_list = keyphrase.split()
			#movie_id_list = movie_id.split()
			keyphrases.append(keyphrase_list)
			movie_ids.append(movie_id)
	#print keyphrases
	#print movie_ids

	if request.method == 'POST':
		print "form"
		keyword_query = request.form['keyword-search']
		print keyword_query
		query_list = keyword_query.split()
		for i, keyphrase_list in enumerate(keyphrases):
			if all(x in query_list for x in keyphrase_list):
				print "id: "
				print movie_ids[i]
				return redirect(url_for('search.search_route', movieIds=movie_ids[i]))
	options = {
	}
	return render_template("index.html", **options)	