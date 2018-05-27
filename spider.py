import urllib, urllib2
from urlparse import *
from tasks import *
import ntpath

# Main spider class
class Spider:

    project_name = ''
    base_url = ''
    site = ''
    domain_name = ''

    out_path = ''

    queue_file = ''
    crawled_file = ''

    queue = set()
    crawled = set()

    downloaded = set()

    def __init__(self, project_name, base_url, output_folder):
        Spider.project_name = project_name
        Spider.base_url = base_url

        urlinfo = urlsplit(base_url)
        Spider.site = urlinfo.netloc
        Spider.domain_name = urlinfo.scheme + '://' + urlinfo.netloc
        Spider.current_dir = str(urlinfo.path).rsplit('/', 1)[0] + '/'

        Spider.out_path = output_folder + '/' + project_name + Spider.current_dir

        self.boot()
        self.crawl_page('First spider', Spider.base_url)

    # Creates directory and files for project on first run and starts the spider
    @staticmethod
    def boot():
        init_path(Spider.out_path)
        Spider.queue.add(Spider.base_url)

    # Updates user display, fills queue and updates files
    @staticmethod
    def crawl_page(thread_name, page_url):
        if page_url not in Spider.crawled:
            print(thread_name + ' now crawling ' + page_url)
            task = Tasks(page_url, Spider.out_path, Spider.downloaded)

            for u in task.get_downloaded_file_set() :
                Spider.downloaded.add(u)

            links = task.get_links()
            for url in links:
                if (filter_query(url) in Spider.queue) or (filter_query(url) in Spider.crawled):
                    continue

                urlinfo = urlparse(url)
                if Spider.site == urlinfo.netloc :
                    Spider.queue.add(filter_query(url))

            Spider.queue.remove(filter_query(page_url))
            Spider.crawled.add(filter_query(page_url))
