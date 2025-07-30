"""
# pipreqs : to generate reqs.txt
# why not to use pip freeze > requirements.txt ( the catch is envdev)
https://www.idiotinside.com/2015/05/10/python-auto-generate-requirements-txt/
"""
# https://blog.jonlu.ca/posts/async-python-http
# https://stackoverflow.com/questions/38252434/beautifulsoup-to-find-a-link-that-contains-a-specific-word
# https://stackoverflow.com/questions/63494930/beautifulsoup-match-empty-class

__author__ = 'Matar'
from urllib.parse import urlparse
import os
import json
import string
import sys
import re
from time import time, sleep
from traceback import print_tb
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import aiohttp
import asyncio
import platform
if platform.system()=='Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
import logging
logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', stream = sys.stdout)
logger = logging.getLogger()

main_url = 'https://www.imdb.com'
rating_list_url = '/user/ur56605022/ratings'
#'https://www.imdb.com/user/ur56605022/ratings?ref_=nv_usr_rt_4'
#requests_cache.install_cache('imdb_cache', backend='sqlite', expire_after=1000)


class Helpers:
    def __init__(self, **kwargs):
        self.args = kwargs

    def request(self) :
        if self.args.get('url') is None:
            raise ValueError('No URL was passed')
        try :
            resp = requests.get(self.args['url'])
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)
        return resp

    def soup(self):
        if self.args.get('movie_html') is None:
            raise ValueError('No html object was passed')
        soup = BeautifulSoup(self.args['movie_html'], 'html.parser')
        return soup
    
    def pages_to_scrape(self):
        # if not all(elem in {'key1','key2'} for elem in self.args.keys()):
        #     raise ValueError('No html object was passed')

        if self.args.get('main_url') is None or self.args.get('rating_list_url') is None:
            raise ValueError('Missing required params')

        main_url = self.args['main_url']
        rating_list_url = self.args['rating_list_url']

        # first page link
        pages = [urljoin(main_url, rating_list_url)]
        first_pages = pages[0]

        # find all other pages links
        while True:
            self.args['url'] = first_pages
            self.args['movie_html'] = self.request().content
            soup = self.soup()
            if soup.find_all("a", class_='flat-button lister-page-next next-page') :
                for item in soup.find_all("a", class_='flat-button lister-page-next next-page') :
                    pages.append(urljoin(main_url, item['href']))
                first_pages = pages[-1]
            else :
                break
        return pages

    @staticmethod
    def get_ids_names(pages):
        # movies_names = {}
        movies_names = []
        for url in pages:
            r = requests.get(url)
            soup = BeautifulSoup(r.content, 'html.parser')
            movie_html = soup.find_all("div", class_='lister-item mode-detail')
            for item in movie_html:
                movies_names.append(MovieParserV1(item).movie_details())
        return movies_names

class MovieParserV1:
    def __init__(self, item) -> None:
        self.item = item
        self._parse_id = item.find(class_='lister-item-image ribbonize')['data-tconst']

    def _parse_name(self) -> string:
        try:
            movie_name = self.item.find(class_='lister-item-header').find("a").get_text().strip()
            if self._parse_id == 'tt3758814':
                movie_name = 'The Ice Road'
            if self._parse_id == 'tt11083552':
                movie_name = 'Wrath of Man'
        except:
            logger.warning(f"could not parse movie name for {self._parse_id} - setting defaul movie_name=NA")
            movie_name = 'NA'
        return str(movie_name)

    def _parse_year(self) -> string:
        #TODO: Find a better generic way to get release year
        try:
            year = self.item.find(class_='lister-item-year text-muted unbold').get_text().strip()
            year = re.sub(r'[^0-9]', '', year)
        except:
            logger.warning(f"could not parse year for {self._parse_id} - setting defaul year=NA")
            year = 0
        return int(year)
    
    def _parse_certificate(self) -> string:
        # if self._parse_id == 'tt0094894':
        #     print(self.item)
        #     exit()
        try:
            movie_certificate = self.item.find(class_='certificate').get_text().strip()
        except:
            logger.warning(f"could not parse movie certificate for {self._parse_id} - setting defaul movie_certificate=NA")
            movie_certificate = 'NA'
        return movie_certificate
    
    def _parse_runtime(self) -> string:
        #TODO: Find a better way to get convert runtime to mintues
        try:
            movie_runtime = self.item.find(class_='runtime').get_text().strip()
        except:
            logger.warning(f"could not parse movie runtime for {self._parse_id} - setting defaul movie_runtime=NA")
            movie_runtime = 'NA'
        return movie_runtime
    
    def _parse_genre(self) -> string:
        try:
            movie_genre = self.item.find(class_='genre').get_text().strip()
            genre_list = [x.strip() for x in movie_genre.split(",")]
        except:
            logger.warning(f"could not parse movie name for {self._parse_id} - setting defaul genre_list=['NA]")
            genre_list = ['NA']
        return genre_list
    
    def _parse_rating(self) -> int:
        try:
            #print(self.item.find(class_='ipl-rating-widget'))
            rating = self.item.find('span', class_='ipl-rating-star__rating').get_text()
        except:
            logger.warning(f"could not parse rating for {self._parse_id} - setting defaul rating=NA")
            rating = 0
        return int(float(rating))
    
    def _parse_desc(self) -> string:
        try:
            desc = self.item.find('p', class_="").get_text().strip()
        except:
            logger.warning(f"could not parse desc for {self._parse_id} - setting defaul desc=NA")
            desc="NA"
        return desc
    
    def _parse_vote(self) -> int:
        try:
            vote = self.item.find('span', {'name':'nv'})['data-value'].strip()
        except:
            logger.warning(f"could not parse desc for {self._parse_id} - setting defaul vote=NA")
            vote="NA"
        return int(vote)
    
    def _parse_people(self) -> string:
        try:
            people = self.item.find('p', class_="text-muted text-small").get_text().strip()
            print(people)
        except:
            logger.warning(f"could not parse desc for {self._parse_id} - setting defaul desc=No description")
            people="NA"
        return people

    def _parse_poster(self) -> string:
        try:
            poster = self.item.find(class_='lister-item-image ribbonize').find('a').find('img')['loadlate']
            poster_url = poster.split('_V1_')[0] + "_V1_.jpg"
        except:
            logger.warning(f"could not parse poster url for {self._parse_id} - setting defaul desc=NA")
            poster_url="NA"
        return poster_url.strip()
    
    def movie_details(self):
        logger.info(f"- parsing movie with ID {self._parse_id}")
        details = {
            "movie_id" : self._parse_id,
            "movie_url": f"https://www.imdb.com/title/{self._parse_id}",
            "name": self._parse_name(),
            "year" : self._parse_year(),
            "certificate": self._parse_certificate(),
            "runtime": self._parse_runtime(),
            "genre": self._parse_genre(),
            "rating" : self._parse_rating(),
            "desc" : self._parse_desc(),
            "poster" : self._parse_poster(),
            "vote": self._parse_vote(),
            }
        return details
    
def main():
    # Pages
    logger.info("- getting pages to scrap ..")
    help_pages = Helpers(main_url=main_url, rating_list_url=rating_list_url)
    pages = help_pages.pages_to_scrape()
    logger.info(f"- we have ({len(pages)}) main pages to loop throug.")

    # get movies names and ids
    logger.info("- started parsing movines details")
    movies_details = Helpers.get_ids_names(pages)

    logger.info("- wrtiting movies details to JSON file")
    sync_movies_full = os.path.abspath(os.path.realpath(os.path.join(os.path.dirname('resource'), 'resource/sync_movies_full.json')))
    with open(sync_movies_full, "w+") as f:
        json.dump(movies_details, f, indent=4)

if __name__ == "__main__":
    main()