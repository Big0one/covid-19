import re
import os
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

headers = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) snap Chromium/83.0.4103.106 Chrome/83.0.4103.106 Safari/537.36"
target_keywords = [
    "করোনা",
    "করোনায়",
    "করোনাতে",
    "করোনার",
    "কোভিড-১৯",
    "উহান-ভাইরাস",
    "উহান-ভাইরাসে",
    "লকডাউনে",
    "লকডাউন",
    "কোয়ারেন্টাইন",
    "কোয়ারেন্টাইনে",
]  # add keywords here
websites = [
    "https://jamuna.tv",
    "https://bangla.bdnews24.com",
    "https://somoynews.tv",
    "https://prothomalo.com",
    "https://www.jugantor.com/",
    "https://www.thedailystar.net/bangla",
]
news_list = []
data_file = os.getcwd() + "/data/corona_news_bn.csv"


def scrape_content(content):
    return BeautifulSoup(
        BeautifulSoup(content, "html.parser").prettify(), "html.parser"
    )


def scrape_url(url):
    try:
        page = requests.get(url, headers)
        page.raise_for_status()
        soup = BeautifulSoup(page.content, "html.parser")
        soup = BeautifulSoup(soup.prettify(), "html.parser")
        return soup
    except:
        return BeautifulSoup("<html></html>", "html.parser").prettify()


def get_valid_link(url):
    parse_url = urlparse(url, "http")
    if parse_url.path is not None:
        url = parse_url.geturl()
        regex = re.compile(
            r"^(?:http|ftp)s?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        if re.match(regex, url):
            return url


def get_news():
    for url in websites:
        soup = scrape_url(url)
        links = soup.find_all("a")
        for link in links:
            news_link = get_valid_link(str(link.get("href")))
            news_heading = link.get_text().strip()

            if not news_link:
                news_link = urlparse(urlparse(url).hostname, "http").geturl() + str(
                    link.get("href")
                )

            title_words = news_heading.split()
            if set(target_keywords).intersection(set(title_words)):
                news_list.append({"Heading": news_heading, "Link": news_link})

    return news_list


def store_news_in_csv(item):
    with open(data_file, "a+", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["Heading", "Link"])
        writer.writerow(item)


if __name__ == "__main__":
    get_news()
    for news in news_list:
        store_news_in_csv(news)
