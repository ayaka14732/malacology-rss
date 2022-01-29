import sys
from urllib.request import urlretrieve

xml_path = sys.argv[1]

urlretrieve('https://diary.malacology.net/index.xml', xml_path)
