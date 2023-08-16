########################
# please DO NOT USE THIS
########################

"""
# pipreqs : to generate reqs.txt
# why not to use pip freeze > requirements.txt ( the catch is envdev)
https://www.idiotinside.com/2015/05/10/python-auto-generate-requirements-txt/
"""
# https://blog.jonlu.ca/posts/async-python-http


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
        movies_names = {}
        for url in pages:
            content = requests.get(url).content
            soup = BeautifulSoup(content, 'html.parser')
            movie_html = soup.find_all("div", class_='lister-item mode-detail')
            for item in movie_html:
                movies_names[item.find(class_='lister-item-image ribbonize')['data-tconst']] = item.find("h3", class_='lister-item-header').find("a").get_text()
        return movies_names

class AsyncCrawler:
    def __init__(self, urls):
        self.conn = aiohttp.TCPConnector(limit_per_host=100, limit=0, ttl_dns_cache=300)
        self.PARALLEL_REQUESTS = 10
        self.urls = urls
    
    async def gather_with_concurrency(self):
        results = []
        semaphore = asyncio.Semaphore(self.PARALLEL_REQUESTS)
        session = aiohttp.ClientSession(connector=self.conn)

        # heres the logic for the generator
        async def get(url):
            async with semaphore:
                async with session.get(url, ssl=False) as response:
                    logger.info(f"- processing  {url}")
                    binary_resp = await response.read()
                    soup = Helpers(movie_html=binary_resp).soup()
                    movie = MovieParser(soup, url).movie_details()
                    results.append(movie)
        await asyncio.gather(*(get(url) for url in self.urls))
        await session.close()
        return results

class MovieParser:
    def __init__(self, soup, movie_url=None) -> None:
        self.soup = soup
        self.movie_url = movie_url

    def _parse_id(self) -> string:
        return str(urlparse(self.movie_url).path.split('/')[2])

    def _parse_name(self) -> string:
        try:
            movie_name = self.soup.find("h1", {'data-testid':'hero-title-block__title'}).get_text()
        except:
            logger.warning(f"could not parse movie name for {self.movie_url} - setting defaul movie_name=No name")
            movie_name = 'No name'
        return str(movie_name)

    def _parse_year(self) -> string:
        #TODO: Find a better generic way to get release year
        try:
            year = self.soup.find(class_='ipc-inline-list__item').find("a").get_text()
        except:
            logger.warning(f"could not parse year for {self.movie_url} - setting defaul year=2000")
            year = 2000
        return str(year)
    
    def _parse_rating(self) -> string:
        try:
            rating = self.soup.find(class_=re.compile('^AggregateRatingButton__RatingScore-sc')).get_text()
        except:
            logger.warning(f"could not parse rating for {self.movie_url} - setting defaul rating=6")
            rating = '6'
        return str(rating)[0]
    
    def _parse_desc(self) -> string:
        try:
            desc = self.soup.find(class_=re.compile('^GenresAndPlot__TextContainerBreakpointXS')).get_text()
        except:
            logger.warning(f"could not parse desc for {self.movie_url} - setting defaul desc=No description")
            desc="No description"
        return str(desc)

    def _parse_poster(self) -> string:
        try:
            poster = self.soup.find(class_='ipc-image')["src"]
            #poster_url = re.sub('_QL75_UX190_CR0,0,190,281_', '_', poster)
            poster_url = re.split(r'QL75_', poster)[0]
        except:
            logger.warning(f"could not parse poster url for {self.movie_url} - setting defaul desc=www.matar.jpg")
            poster_url="www.matar.com"
        return str(poster_url+'.jpg')
    
    def movie_details(self):
        details = {
            "movie_id" : self._parse_id(),
            "movie_url": self.movie_url,
            "name": self._parse_name(),
            "year" : self._parse_year(),
            "rating" : self._parse_rating(),
            "desc" : self._parse_desc(),
            "poster" : self._parse_poster()
            }
        return details


def main():
    # Pages
    logger.info("getting pages to scrap ..")
    help_pages = Helpers(main_url=main_url, rating_list_url=rating_list_url)
    pages = help_pages.pages_to_scrape()
    logger.info(f"we have {len(pages)} main pages to loop throug .. I'll sleep for 10 seconds")
    sleep(10)

    # get movies names and ids
    logger.info("started building movines names and ids .. then sleep for 60 second")
    movies_names = Helpers.get_ids_names(pages)
    sleep(60)

    # sample 
    logger.info(f"we got {len(movies_names)},here is a sample output :")
    for key,value in movies_names.items():
        print(f"id: {key}, and movie name: {value}")
        break

    # dump the result locally   
    logger.info(f"Now wrtiting to JSON file")
    movies_names_ids = os.path.abspath(os.path.realpath(os.path.join(os.path.dirname('resource'), 'resource/movies_names_ids.json')))
    with open(movies_names_ids, "w") as f:
        json.dump(movies_names, f)

    # Asynch
    urls = [f"{main_url}/title/{key}" for key in movies_names]
    logger.info(f"Starting Async crawler")
    Crawler = AsyncCrawler(urls)
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(Crawler.gather_with_concurrency())
    Crawler.conn.close()

    logger.info("wrtiting to JSON file")
    async_movies_full = os.path.abspath(os.path.realpath(os.path.join(os.path.dirname('resource'), 'resource/async_movies_full.json')))
    with open(async_movies_full, "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    main()