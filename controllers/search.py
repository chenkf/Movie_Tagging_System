from flask import *
import csv

search = Blueprint('search', __name__, template_folder='template')

@search.route('/keyword-search-result', methods=['GET', 'PUT', 'POST'])
def search_route():
	titles = []
	ids = []
	pic_urls = []
	with open('titles_ids_images.csv','r') as f:
		reader = csv.reader(f)
		for title, movie_id, url in reader:
			titles.append(title)
			ids.append(movie_id)
			pic_urls.append(url)

	# print titles
	# print ids
	# print pic_urls		

	movieIds = request.args.get('movieIds')
	movie_id_list = movieIds.split()
	movie_info = {}
	for i, movie_id in enumerate(ids):
		if movie_id in movie_id_list:
			movie_info[titles[i]] = pic_urls[i]
	print movie_info		
	options = {
		"movie_info": movie_info
	}
	return render_template("keyword_search.html", **options)
	#movieIds = json.loads(movieIds)
