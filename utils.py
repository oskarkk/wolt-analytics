try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract as tess

import json
from glob import glob
import pprint


data = { 'payouts': {}, 'deliveries': {} }


def save():
  with open('data.json', 'w') as f:
    json.dump(data, f)

def read():
  with open('data.json', 'r') as f:
    return json.load(f)


def ocr(*paths):
  pages = []
  for path in paths:
    # --psm 4 - Assume a single column of text of variable sizes.
    # 3 - Fully automatic page segmentation, but no OSD. (Default)
    # https://github.com/tesseract-ocr/tesseract/blob/master/doc/tesseract.1.asc
    page = tess.image_to_string(Image.open(path), lang='eng+pol', config='--psm 4')
    pages.append(page[:-1]) # [:-1] bo na końcu jest znak końca strony czy coś: \x0c
  return pages


def save_pages(pages, name):
  with open(name+'.json', 'w') as f:
    json.dump(pages, f)

def read_pages(name):
  with open(name+'.json', 'r') as f:
    return json.load(f)


def pp(s):
  pprint.pp(s, sort_dicts=True)

def gl(s):
  return sorted(glob(s))
