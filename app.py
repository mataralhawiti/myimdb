from flask import Flask, render_template
import os
import json
from datetime import date
import logging
logging.basicConfig(level=logging.DEBUG)

# create the app object
app = Flask(__name__)

# load the movies data from local JSON
SOURCE = "dummy"
movies = os.path.abspath(os.path.realpath(os.path.join(os.path.dirname('resource'), f"resource/{SOURCE}.json")))
with open(movies, 'r') as f:
    movies = [i for i in json.load(f)]

@app.route('/', methods=['GET', 'POST'])
#@app.route('/home')
def index():
    return render_template('index.html', \
        title='Home page',\
        movies= movies, \
        count= len(movies) , \
        last_updated_date = date.today().strftime("%m-%d-%Y")
        )

# start the server with 'run()' method
if __name__ == '__main__' :
    app.run(debug=True, host='0.0.0.0')