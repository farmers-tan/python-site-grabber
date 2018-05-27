import threading
from Queue import *
from spider import *
from tasks import *

# main file to implement the crawler
project = 'inews'
domain = 'http://nayem.cottonkraft.com/inews_v1.0/'
url = 'http://nayem.cottonkraft.com/inews_v1.0/index.html'
output_folder = 'downloads'

threads = 3
queue = Queue()

Spider(project, url, output_folder)
# print(html.prettify())

# Generate Threads
def generate_threads() :
    for _ in range(threads):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()

def work() :
     while True:
        url = queue.get()
        Spider.crawl_page(threading.current_thread().name, url)
        queue.task_done()

# Each queued link is a new job
def create_jobs():
    for link in Spider.queue:
        queue.put(link)
    queue.join()
    crawl()

# Check if there are items in the queue, if so crawl them
def crawl() :
    queued_links = Spider.queue
    if len(queued_links) > 0:
        print(str(len(queued_links)) + ' links in the queue')
        create_jobs()

generate_threads()
crawl()
