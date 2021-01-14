"""
    Simple Google Image Scraper.
    NOTE: Disclaimer: The Original implementation of Magic is fully credited to @AdamHupp.
    I modified it in order to better suit the purpose of this simple web scraper.
    The Package can be found at --> https://pypi.org/project/python-magic/
    Repository --> https://github.com/ahupp/python-magic
    The Actual Script was taken from ---> https://github.com/julian-r/python-magic/blob/master/magic/magic.py
    which as fixes for Windows 64-bit.
"""

import os
import urllib
import requests
from urllib.parse import quote
import random
from requests.exceptions import ReadTimeout
import sys
import os.path
import ctypes.util
import threading
import zipfile
import io
import pathlib
from ctypes import c_char_p, c_int, c_size_t, c_void_p

# =============================== <  libmagic.dll Imports > =============================== #
# NOTE: Cross Platform.
libmagic = None
# Lfind magic or magic1
dll = ctypes.util.find_library('magic') or ctypes.util.find_library('magic1') or ctypes.util.find_library('cygmagic-1')

bin_dist_path = os.path.join(os.path.dirname(__file__), 'libmagic')
if os.path.isdir(bin_dist_path):
    if sys.platform == 'win32':
        dll = os.path.abspath(os.path.join(bin_dist_path, 'libmagic.dll'))
    default_magic_file = os.path.join(bin_dist_path, 'magic.mgc')

if dll:
    libmagic = ctypes.CDLL(dll)
if not libmagic or not libmagic._name:
    platform_to_lib = {'linux': ['libmagic.so.1']}
    platform = 'linux'
    for dll in platform_to_lib.get(platform, []):
        try:
            libmagic = ctypes.CDLL(dll)
            break
        except OSError:
            pass

if not libmagic or not libmagic._name:
    # It is better to raise an ImportError since we are importing magic module
    raise ImportError('failed to find libmagic.  Check your installation')

magic_t = ctypes.c_void_p



class MagicException(Exception):
    def __init__(self, message):
        super(MagicException, self).__init__(message)
        self.message = message


class Magic:
    def __init__(self, mime=False):
        self.flags = MAGIC_NONE
        if mime:
            self.flags |= MAGIC_MIME

        self.cookie = magic_open(self.flags)
        self.lock = threading.Lock()
        magic_load(self.cookie, None)

    def from_buffer(self, buf):
        """
        Identify the contents of `buf`
        """
        with self.lock:
            try:
                return magic_buffer(self.cookie, buf).decode('utf-8')
            except MagicException as e:
                return self._handle509Bug(e)

    def _handle509Bug(self, e):
        if e.message is None and (self.flags & MAGIC_MIME):
            return "application/octet-stream"
        else:
            raise e

# =============================== <  Error Handler > =============================== #
def errorcheck_null(result, func, args):
    if result is None:
        err = magic_error(args[0])
        raise MagicException(err)
    else:
        return result


def errorcheck_negative_one(result, func, args):
    if result == -1:
        err = magic_error(args[0])
        raise MagicException(err)
    else:
        return result


magic_open = libmagic.magic_open
magic_open.restype = magic_t
magic_open.argtypes = [c_int]

magic_error = libmagic.magic_error
magic_error.restype = c_char_p
magic_error.argtypes = [magic_t]

_magic_file = libmagic.magic_file
_magic_file.restype = c_char_p
_magic_file.argtypes = [magic_t, c_char_p]
_magic_file.errcheck = errorcheck_null

_magic_buffer = libmagic.magic_buffer
_magic_buffer.restype = c_char_p
_magic_buffer.argtypes = [magic_t, c_void_p, c_size_t]
_magic_buffer.errcheck = errorcheck_null


def magic_buffer(cookie, buf):
    return _magic_buffer(cookie, buf, len(buf))


_magic_load = libmagic.magic_load
_magic_load.restype = c_int
_magic_load.argtypes = [magic_t, c_char_p]
_magic_load.errcheck = errorcheck_negative_one


def magic_load(cookie, filename):
    return _magic_load(cookie, None)

################
# ---> CONSTANTS
################

MAGIC_NONE = 0x000000  # No flags
MAGIC_MIME = 0x000010  # Return a mime string
MAGIC_ERROR = 0x000200 # Handle ENOENT etc as real errors

# NOTE: Current Google URL for seach Images. May change in the Future.
# This can also be used
# URL_ROOT = 'https://www.google.com/search?q='
# URL_END = '&source=lnms&tbm=isch'

BASE_URL = 'https://www.google.com/search?q='
GOOGLE_PICTURE_ID = '''&biw=1536&bih=674&tbm=isch&sxsrf=ACYBGNSXXpS6YmAKUiLKKBs6xWb4uUY5gA:1581168823770&source=lnms&sa=X&ved=0ahUKEwioj8jwiMLnAhW9AhAIHbXTBMMQ_AUI3QUoAQ'''
HEADERS = {
    'User-Agent':
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
}
SCANNER_COUNTER = None


def generate_search_url(keywords):
    keywords_to_search = [str(item).strip() for item in keywords.split(',')][0].split()
    keywords_count = len(keywords_to_search)
    if keywords_count > 3:  # Remove additional Keyword if added
        keywords_to_search = keywords_to_search[:3]
        keywords_count = 3
    return keywords_to_search, keywords_count


def generate_urls(search):
    """Generates a URLS in the correct format that brings to Google Image seearch page"""
    return [(BASE_URL + quote(word) + GOOGLE_PICTURE_ID) for word in search]


def check_webpage(url):
    checked_url = None
    try:
        request = requests.get(url, allow_redirects=True, timeout=10)
        if 'html' not in str(request.content):
            checked_url = request
    except ReadTimeout as err:
        print(err)
        pass
    return checked_url


def scan_webpage(webpage, extensions, timer):
    """Scans for pictures to download based on the keywords"""
    global SCANNER_COUNTER
    scanner = webpage.find
    found = False
    counter = 0
    while counter < timer:
        new_line = scanner('"https://', SCANNER_COUNTER + 1)  # How Many New lines
        SCANNER_COUNTER = scanner('"', new_line + 1)  # Ends of line
        buffor = scanner('\\', new_line + 1, SCANNER_COUNTER)
        if buffor != -1:
            object_raw = webpage[new_line + 1:buffor]
        else:
            object_raw = webpage[new_line + 1:SCANNER_COUNTER]
        if any(extension in object_raw for extension in extensions):
            found = True
            break
        counter += 1
    if found:
        object_ready = check_webpage(object_raw)
        return object_ready


class Downloader:
    """
        Main Downloader
        ::param extension:iterable of Files extensions
    """

    def __init__(self):
        self._extensions = {'.jpg', '.png', '.ico', '.gif', '.jpeg'}
        self._directory = "scrapy_images/"
        self.get_dirs = set()

    def _download_page(self, url):
        req = urllib.request.Request(url, headers=HEADERS)
        resp = urllib.request.urlopen(req)
        resp_data = str(resp.read())
        return resp_data

    def search_urls(self, keywords, limit):
        cache_out = {}
        search, count = generate_search_url(keywords)
        urls_ = generate_urls(search)
        timer = 1000

        i = 0
        while i < count:
            global SCANNER_COUNTER
            SCANNER_COUNTER = -1
            url = urls_[i]
            path = self.generate_dir(search[i])
            raw_html = self._download_page(url)  # Download the entire page from the google Picture search
            for _ in range(limit):
                webpage_url = scan_webpage(raw_html, self._extensions, timer)
                if webpage_url:
                    file_name = Downloader.gen_fn(webpage_url, search[i])
                    cache_out[file_name] = [path, webpage_url]
                else:
                    pass
            i += 1

        if not cache_out:
            print('===' * 15 + ' < ' + 'NO PICTURES FOUND' + ' > ' + '===' * 15)
        return cache_out

    def download(self, keywords, limit=None):
        """Download is has 3 Main steps:
            1. Search che URLS and download the Images
            2. Creates Folder and Sub Folder System + saves each downloaded images in it.
            3. Iterate within each sub folder and zip each image then remove the Image and finally the SubDirectory.
            We don't want the Files to be saved on the server.
        """
        content = self.search_urls(keywords, limit)
        paths = set()
        for name, (path, url) in content.items():
            paths.add(path)
            with open(os.path.join(path, name), 'wb') as file:
                file.write(url.content)

        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as z:
            for path in paths:
                base_path = pathlib.Path(path)

                for fname in base_path.iterdir():
                    data = zipfile.ZipInfo(name) # TODO
                    data.compress_type = zipfile.ZIP_STORED
                    z.write(fname)  # NOTE: Add Image to Zip Folder
                    fname.unlink()  # NOTE: Remove Image from Directory
                base_path.rmdir()   # NOTE: Remove Sub Directory
        memory_file.seek(0)

        return memory_file

    def _create_directories(self, name):
        dir_path = os.path.join(self._directory, name)
        try:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        except OSError:
            raise
        self.get_dirs.update([name])
        return

    def generate_dir(self, dir_name):
        """Generate Path and Directory, also check if Directory exists or not """

        dir_name = dir_name.replace(" ", "_")
        self._create_directories(dir_name)
        return self._directory + dir_name

    @staticmethod
    def gen_fn(check, name):
        """Create a file name string and generate a random identifiers otherwise won't import same pic twice"""
        id = str(hex(random.randrange(1000)))
        mime = Magic(mime=True)
        file_type = mime.from_buffer(check.content)
        file_extension = f'.{file_type.split("/")[1]}'
        file_name = str(name) + "_" + id[2:] + file_extension
        return file_name

