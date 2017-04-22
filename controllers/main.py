from flask import *

#from datetime import datetime
#from collections import namedtuple

main = Blueprint('main', __name__, template_folder='template')

@main.route('/', methods=['GET', 'PUT', 'POST'])
def main_route():
	options = {
	
	}
	return render_template("index.html", **options)