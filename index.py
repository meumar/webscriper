import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from tqdm import tqdm 
import json

import sys  # Import sys module for command-line arguments


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) 
    except ValueError:
        return False

def does_not_start_with_http(url):
    return url and not (url.startswith("http://") or url.startswith("https://"))

def get_main_domain(url):
    parsed_url = urlparse(url)
    domain_parts = parsed_url.netloc.split('.')

    if len(domain_parts) > 1:
        main_domain = '.'.join(domain_parts[-2:])
    else:
        main_domain = parsed_url.netloc

    return main_domain

def web_scrape(url, keyWords = [], searchedUrls = {}):
    try:
        if is_valid_url(url) and url not in searchedUrls:
            req = requests.get(url)
            soup = BeautifulSoup(req.content, 'html.parser')
            mainDomain = get_main_domain(url)
            res = soup.get_text()
            searchedUrls[url] = '\n'.join([line for line in res.splitlines() if line.strip()])
            searchFound = False
            for keyWord in keyWords:
                if keyWord.lower() in res.lower():
                    searchFound = True
            if searchFound:
                nestedUrls = []
                for link in soup.find_all("a"):
                    u = link.get("href")
                    if u not in nestedUrls and u != '/':
                        if does_not_start_with_http(u):
                            u = "http://" + mainDomain + u
                        nestedUrls.append(u)
                        
                if len(nestedUrls) > 0:
                    for nUrl in tqdm(nestedUrls, desc="Processing nested URLs", unit=" URLs"):
                        if nUrl not in searchedUrls:
                            urls = webScripe(nUrl, searchedUrls=searchedUrls) or {}
                            searchedUrls = {**searchedUrls, **urls}
        return searchedUrls
    except:
        return searchedUrls





def main():
    print(sys.argv)
    if len(sys.argv) == 2 and sys.argv[1] == '--help':
        print("Usage: python index.py <URL>, ...keywords")
        return
    if len(sys.argv) < 3:
        print("Usage: python index.py <URL> <keyword1> <keyword2> ...")
        return
    url = sys.argv[1]
    keywords = sys.argv[2:]

    searched_urls = {}
    result = web_scrape(url, keywords, searched_urls)

    file_path = "example.txt"
    formatted_json = json.dumps(result, indent=4)

    with open(file_path, 'w') as file:
        file.write(formatted_json)

    print(f"Text content has been written to '{file_path}'")

if __name__ == "__main__":
    main()
