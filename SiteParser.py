import re, time
from robobrowser import RoboBrowser
import requests
import gzip
from datetime import datetime as dt


class Parser:
    """
    get_all_links_from_sitemap(base_url) - Возвращает все ссылки которые может найти в sitemap-файлах
    open_page(url) - Открывает страницу
    get_all_links_from_page - Возвращает все ссылки с открытой страницы
    """

    USERAGENT = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"

    def __init__(self):

        self.browser = RoboBrowser(history=True, cache=True, user_agent=self.USERAGENT)

    def open_page(self, url):
        self.browser.open(url)
        self.browser.session.headers['Referer'] = url

    @property
    def html(self):

        return str(self.browser.parsed)  # self.browser.select

    def get_all_links_from_page(self):
        links = []
        for tag_a in self.browser.find_all('a'):
            prelink = re.findall(r'href=[\'\"](.*?)[\'\"]', str(tag_a))[0]

            if prelink.startswith('/'):
                link = self.browser.url + prelink[1:]
            else:
                link = prelink

            links.append(link)
        return links

    def get_all_links_from_sitemap(self, base_url):
        """ base_url = 'http://example.com' """

        start_links = ['/robots.txt', '/sitemap.xml', '/sitemap.xml.gz']
        site_links = []
        sitemaps_links = []
        parsed_sitemaps_links = []

        def parse_sitemap(sitemap_url):
            if sitemap_url.endswith('gz'):
                r = requests.get(sitemap_url, stream=True)
                xml_data = gzip.decompress(r.raw.read())

            elif sitemap_url.endswith('xml'):
                r = requests.get(sitemap_url, stream=True)
                xml_data = r.text

            links = re.findall(r'<loc>(.*?)</loc>', str(xml_data))
            for link in links.copy():
                if 'sitemap' in link:
                    sitemaps_links.append(link)
                    links.remove(link)

            parsed_sitemaps_links.append(sitemap_url)
            sitemaps_links.remove(sitemap_url)
            return links

        base_url_list = [base_url + url for url in start_links]

        for url in base_url_list:
            self.browser.open(url)

            if self.browser.response.status_code == 200:
                try:
                    sitemap_url = re.findall(r'[Ss]itemap: (.*)', str(self.browser.select))[0]
                    sitemaps_links.append(sitemap_url)

                except:
                    if 'robots.txt' not in url:
                        sitemaps_links.append(self.browser.url)

        while sitemaps_links:
            for map_link in sitemaps_links.copy():
                if map_link not in parsed_sitemaps_links:

                    print(map_link)
                    site_links.extend(parse_sitemap(map_link))
                else:
                    sitemaps_links.remove(map_link)

        return site_links


if __name__ == '__main__':
    p = Parser()

    base_name = 'lenta.ru'
    # base_name = 'habrahabr.ru'
    # base_name = 'geekbrains.ru'
    # base_name = 'rbc.ru'

    site_links = p.get_all_links_from_sitemap('http://%s' % base_name)


    print(len(site_links))
