from flask import Flask, render_template
import json
import logging
logging.basicConfig(level=logging.DEBUG)

# create the app object
app = Flask(__name__)

# load the movies data from local JSON 
with open(r"resources\movies.json", 'r') as f:
    movies = [i for i in json.load(f)]

# load movies last update date and count from local JSON
with open(r"resources\movies_names.json", 'r') as f:
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


