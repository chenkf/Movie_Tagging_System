from flask import *
import controllers

# Initialize Flask app with the template folder address
app = Flask(__name__, template_folder='templates')

# Register the controllers
app.register_blueprint(controllers.main)
app.register_blueprint(controllers.search)

#listen to port 3000 so you can just run 'python app.py' to start the server
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=3000, debug=True)