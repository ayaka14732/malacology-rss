import sys
import urllib.request

xml_path = sys.argv[1]

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib.request.install_opener(opener)
urllib.request.urlretrieve('https://diary.malacology.net/index.xml', xml_path)
