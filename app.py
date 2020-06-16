from flask import Flask, render_template
import os
import json
import logging
logging.basicConfig(level=logging.DEBUG)

# create the app object
app = Flask(__name__)

# load the movies data from local JSON 
movies = os.path.abspath(os.path.realpath(os.path.join(os.path.dirname('resources'), 'resources/movies.json')))
with open(movies, 'r') as f:
    movies = [i for i in json.load(f)]

# load movies last update date and count from local JSON
movies_names = os.path.abspath(os.path.realpath(os.path.join(os.path.dirname('resources'), 'resources/movies_names.json')))
with open(movies_names, 'r') as f:
    main_json = json.load(f)
    count = main_json["count"]
    last_updated_date = main_json["Last_full_load"]


@app.route('/', methods=['GET', 'POST'])
#@app.route('/home')
def index():
    return render_template('index.html', \
        title='Home page',\
        movies=movies, \
        count = count , \
        last_updated_date = last_updated_date
        )


# start the server with 'run()' method
if __name__ == '__main__' :
    app.run(debug=True, host='0.0.0.0')


