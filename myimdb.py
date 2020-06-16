#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
# pipreqs : to generate reqs.txt
# why not to use pip freeze > requirements.txt ( the catch is envdev)
https://www.idiotinside.com/2015/05/10/python-auto-generate-requirements-txt/
"""

__author__ = 'Matar'
import sys
import re
import json
import datetime
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

main_url = 'http://www.imdb.com'
rating_list_url = '/user/ur56605022/ratings'


def make_request(url) :
	""" get top 250 movies list

	:parm url: main url for 
	:return: conent object
	"""
	try :
		r = requests.get(url)
	except requests.exceptions.RequestException as e:
		print(e)
		print("something is wrong, I could not make a request")
		sys.exit(1)
	return r.content


def links_list():
    """
    get a list of links (pages) that need to scrape

    :retuen: list of urls
    """
    # first page link
    urls = [urljoin(main_url, rating_list_url)]
    first_url = urls[0]

    # find all other pages links
    while True:
        content = make_request(first_url)
        soup = BeautifulSoup(content, 'html.parser')
        if soup.find_all("a", class_='flat-button lister-page-next next-page') :
            for item in soup.find_all("a", class_='flat-button lister-page-next next-page') :
                urls.append(urljoin(main_url, item['href']))
            first_url = urls[-1]
        else :
            break
    return urls


def get_movies_names(urls):
    """
    get a list of all movies names before processing

    :parm: dic of {movie_name : url}
    :return: list of movies names in my moives rating page
    """
    movies_names = {}
    for url in urls:
        content = make_request(url)
        soup = BeautifulSoup(content, 'html.parser')
        movie_html = soup.find_all("div", class_='lister-item mode-detail')
        for item in movie_html:
            movies_names[item.find("h3", class_='lister-item-header').find("a").get_text()] = url
    return movies_names


def get_movies_dtls(urls, movies=None, mode="full") :
    """
    scrape all movies in the rating list, in all pages (urls)

    :param: list of urls
    return: list of dictionaries that contain movie details
    """
    movies_list = []
    movies_names = []

    if mode == "refresh":
        movies, urls = refresh_movies_list()
        with open(r"resources\movies.json", 'r') as f:
            movies_list = json.load(f)

    for index, url in enumerate(urls):
        content = make_request(url)
        soup = BeautifulSoup(content, 'html.parser')
        movie_html = soup.find_all("div", class_='lister-item mode-detail')
        
        for item in movie_html:
            name = item.find("h3", class_='lister-item-header').find("a").get_text()
            if mode == "refresh" and name not in movies:
                break
            movie_id = item.find("div", class_= "lister-item-image ribbonize")["data-tconst"]
            year = item.find("h3", class_='lister-item-header').find(class_="lister-item-year text-muted unbold").get_text()
            rating = item.find("div", class_='ipl-rating-star ipl-rating-star--other-user small').find("span",class_="ipl-rating-star__rating").get_text()
            desc = item.find("div", class_='lister-item-content').find("p",class_='').get_text().strip()
            link = item.find("h3", class_='lister-item-header').find("a")['href']
            poster = movie_poster(link, movie_id)
            
            # build movie dict
            movie_info = {
            "movie_id" : movie_id,
            "name": name,
            "year" : int(re.sub(r'\D', "",year)),
            "rating" : rating ,
            "desc" : desc,
            "poster" : poster
            }

            # our movies list
            movies_list.append(movie_info)
            movies_names.append(name)
            print(name)
            time.sleep(3)

        # sleep before processing next page
        print(f"done processing page {index+1}")
        time.sleep(20)
    return movies_list

def movie_poster(link, movie_id):
	# get movie details to extact high quilty poster page
    movie_dtls_req = make_request(main_url+link)
    movie_soup = BeautifulSoup(movie_dtls_req, 'html.parser')
    movei_dtls = movie_soup.find("div", class_='poster').find("a")['href'] # movei_dtls -> "/title/tt0443706/mediaviewer/rm3361097728"

    # extact high quilty poster url
    poster_req = make_request(main_url+movei_dtls)
    poster_soup = BeautifulSoup(poster_req, 'html.parser')
    poster_link = poster_soup.find_all("script")
    tag = poster_link[1].get_text().strip()
    tag = tag[:-1]
    tag = tag.replace('window.IMDbMediaViewerInitialState = ', '')
    tag = tag.replace("'mediaviewer'", '"mediaviewer"')
    data = json.loads(tag)
    data1 = data["mediaviewer"]["galleries"][movie_id]["allImages"]
    poster = ''
    for i in data1:
        if i.get("id") == movei_dtls.split('/')[-1]:
            poster = i.get("src")
            break
    return poster


def refresh_movies_list():
    """
    """
    movies_names = get_movies_names(links_list())
    # load movies name that have been processed before
    with open(r"resources\movies_names.json", 'r') as f:
        main_json = json.load(f)["movies_names"]
    
    new_moives = list(set(movies_names.keys()).symmetric_difference(set(main_json)))
    urls = [movies_names[movie]  for movie in new_moives if movie in movies_names.keys()]
    return new_moives, list(set(urls))

def update_movies_json(movies_list):
    """
    write out movies details to movies.json.
    and update movies_names.json
    
    param: list of movies
    return: None
    """
    # movies.json, main file with all details
    with open(r"resources\movies.json", "w") as f:
        json.dump(movies_list, f)

    # movies_names.json used for lookup in refresh
    with open(r"resources\movies_names.json", "w") as f:
        json.dump(dict(count=len(movies_list), \
            Last_full_load= datetime.date.today().strftime("%m-%d-%Y"), \
            movies_names = [movie["name"] for movie in movies_list] ), f)

def main():
    urls = links_list()
    movies = get_movies_dtls(urls)
    update_movies_json(movies)

    # # write out movies to JSON
    # with open(r"resources\movies.json", "w") as f:
    #     json.dump(movies, f)
    # refresh_movies_list()

    # urls = links_list()
    # names = get_movies_names(urls)
    # movies = [i for i in names.keys()]

    # with open(r"resources\movies_names.json", "w") as f:
    #     json.dump(dict(count=267, \
    #         Last_full_load= datetime.date.today().strftime("%m-%d-%Y"), movies_names = movies), f)

    # names, urls = refresh_movies_list()
    # print(names)
    # print(urls)

    


if __name__ == "__main__" :
	main()
