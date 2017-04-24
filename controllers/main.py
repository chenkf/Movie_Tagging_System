from flask import *
import csv
from nltk.stem import WordNetLemmatizer

#from datetime import datetime
#from collections import namedtuple

main = Blueprint('main', __name__, template_folder='template')

@main.route('/', methods=['GET', 'PUT', 'POST'])
def main_route():

	keyphrases = []
	movie_ids = []
	with open('inverseIndex_singlerank.csv','r') as f:
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
		retrieved_movie_ids = ''
		lemmatizer = WordNetLemmatizer()
		for i, keyphrase_list in enumerate(keyphrases):
			keyphrase_list = [lemmatizer.lemmatize(x) for x in keyphrase_list]
			# all terms in query must be contained by keyphrase_list
			if all(lemmatizer.lemmatize(x) in keyphrase_list for x in query_list):
				# print "id: "
				# print movie_ids[i]
				retrieved_movie_ids += movie_ids[i] + ' '
		print "id: "
		print retrieved_movie_ids
		if len(retrieved_movie_ids) > 1:
			return redirect(url_for('search.search_route', movieIds=retrieved_movie_ids))
	options = {
	}
	return render_template("index.html", **options)