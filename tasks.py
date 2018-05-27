import urllib, urllib2
from urlparse import *
import requests
from bs4 import BeautifulSoup
import ntpath
import os
import sys as Sys
import re


class Tasks :
    domain = ''
    current_web_dir = ''
    valid_ext = []

    html = BeautifulSoup('')
    links = set()

    css_files = set()

    def __init__(self, url, out_path, downloaded_files) :
        self.url = url
        self.out_path = out_path
        self.downloaded_files = downloaded_files

        if self.get_source(url) :
            urlinfo = urlsplit(url)
            self.domain = urlinfo.scheme + '://' + urlinfo.netloc
            self.current_web_dir = url.rsplit('/', 1)[0] + '/'

            self.valid_ext = ['.html', '.php']

            self.save_page(url)
            self.do_task()

    def get_source(self, url) :
        try:
            response = urllib2.urlopen(url)
        except Exception as e:
            print('Opening Url failed : [' + url + ']')
            return False

        self.url_response_info = response.info()
        self.html = BeautifulSoup(response.read())
        return True

    def do_task(self) :
        self.download_css()
        self.download_img()
        self.download_js()

    def get_links(self) :
        links = self.html('a')
        for a in links:
            attrs = a.attrs
            if 'href' in attrs.keys() :
                href = a['href']
                path = str(urlparse(urljoin(self.domain, a['href'].strip())).path)
                location, filename = ntpath.split(path)
                filename , ext = os.path.splitext(filename)
                if ext in self.valid_ext :
                    self.links.add(urljoin(self.current_web_dir, a['href']))

        return self.links



    def download_css(self) :
        css = self.html('link')
        total = len(css)
        counter = 0

        for link in css :
            attrs = link.attrs

            counter +=1
            progress = counter*100/total

            if 'href' in attrs.keys() :
                link['href'] = filter_query(link['href'], isUrl=False)
                pathData = path_data(link['href'])
                init_path(self.out_path + '/' + pathData[0] + '/')
                _path = urljoin(self.current_web_dir, link['href'])

                if _path not in self.downloaded_files:
                    try :
                        download_file(_path, self.out_path +  link['href'])

                        f = open(self.out_path +  link['href'],'r')
                        contents = f.read()
                        f.close()
                        find = re.findall(r"url\(['\"]?(.*?)['\"]?\)", contents)

                        if len(find) > 0 :
                            t = len(find)
                            i = 0
                            for f in find:
                                _p = self.current_web_dir + pathData[0] + '/'
                                file_path = urljoin(_p, str(f))
                                download_path = urljoin(str(self.out_path + pathData[0] + '/'), str(f))
                                download_path = urlparse(download_path).path
                                if file_path not in self.downloaded_files:
                                    if urlparse(f).scheme == '' :
                                        try :
                                            init_path(path_data(download_path)[0])
                                            download_file(file_path, download_path)
                                        except Exception as e:
                                            print(str(e) + 'Download file failed : [' + link['href'] +'] ==>' + file_path )
                                    self.downloaded_files.add(file_path)
                                p = i*100/t
                                Sys.stdout.write("Downloading CSS : %d%%  [%d%%] \r" % (progress, p) )
                                Sys.stdout.flush()

                    except Exception as e:
                        print('Download CSS failed [' +  link['href'] + ']')
                    self.downloaded_files.add(_path)

            Sys.stdout.write("Downloading stylesheet : %d%%                   \r" % (progress) )
            Sys.stdout.flush()



    def download_js(self) :
        js = self.html('script')
        total = len(js)
        counter = 0

        for script in js :
            attrs = script.attrs
            if 'src' in attrs.keys() :
                script['src'] = filter_query(script['src'], isUrl=False)
                pathData = path_data(script['src'])
                init_path(self.out_path + '/' + pathData[0])
                _path = urljoin(self.current_web_dir, script['src'])

                if _path not in self.downloaded_files:
                    try:
                        download_file(_path, self.out_path +  script['src'])
                    except Exception as e:
                        print('Download JS failed [' +  script['src'] + ']')
                    self.downloaded_files.add(_path)
            counter +=1
            progress = counter*100/total
            Sys.stdout.write("Downloading scripts : %d%%                   \r" % (progress) )
            Sys.stdout.flush()


    def download_img(self) :
        imgs = self.html('img')
        total = len(imgs)
        counter = 0

        for img in imgs :
            attrs = img.attrs
            if 'src' in attrs.keys() :
                img['src'] = filter_query(img['src'], isUrl=False)
                pathData = path_data(img['src'])
                init_path(self.out_path + '/' + pathData[0])
                _path = urljoin(self.current_web_dir, img['src'])

                if _path not in self.downloaded_files:
                    try:
                        download_file(_path, self.out_path +  img['src'])
                    except Exception as e:
                        print('Download Image failed [' +  img['src'] + ']')
                    self.downloaded_files.add(_path)
            counter +=1
            progress = counter*100/total
            Sys.stdout.write("Downloading Images : %d%%                   \r" % (progress) )
            Sys.stdout.flush()



    def save_page(self, url) :
        url = filter_query(url)
        filename = url.split('/')[-1]
        Html_file = open(self.out_path + '/' + filename,"w")
        Html_file.write(str(self.html))
        Html_file.close()


    def get_downloaded_file_set(self) :
        return self.downloaded_files


def download_file(file_url, save_path) :
    download = urllib.URLopener()
    download.retrieve(file_url, save_path)


def init_path(path):
    if not os.path.exists(path):
        os.makedirs(path)

def path_data(path):
    head, tail = ntpath.split(path)
    return [head, tail or ntpath.basename(head)]

def filter_query(url, isUrl=True) :
    urlinfo = urlsplit(url)
    if isUrl :
        return urljoin(urlinfo.scheme + '://' + urlinfo.netloc, urlinfo.path)
    else :
        return urlinfo.path
