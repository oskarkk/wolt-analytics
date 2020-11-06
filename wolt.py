#!/usr/bin/python3 -i

import re
from datetime import datetime
from utils import *
#from pathlib import Path

def payouts(page):
  for line in page.splitlines():
    if ('>' in line) and (line[:3] != 'PLN'):
      parts = re.match('(.*)/(.*)/(.*) PLN(.*) >', line).groups()
      if parts[0] == '01':
        if parts[1] == '01':
          name = str(int(parts[2])-1) + '-12-h2'
        else:
          name = parts[2] + '-' + str(int(parts[1])-1).rjust(2,'0') + '-h2'
      else:
        name = parts[2] + '-' + parts[1] + '-h1'
      value = float(parts[3].replace(',',''))
      data['payouts'].setdefault(name, {})
      data['payouts'][name]['value'] = value

def deliveries(*pages):
  data.setdefault('deliveries', {})
  s = []
  for page in pages:
    page = page.replace('PLNO', 'PLN0')
    s += page.splitlines()
  day = None
  delivery = None
  for line in s:

    print(line.ljust(40), end='')

    # linijka z datą (data przypisywana do wszystkich zamówień aż do znalezienia nast. daty)
    match = re.match('(..)/(..)/(....)$', line)
    if match:
      day = match.groups()[::-1]

    # linijka z restauracją i czasem (data + czas = id zamówienia)
    match = re.match('(.*) (..):(..)$', line)
    if match:
      g = match.groups()
      delivery_id = day[0] + '-' + day[1] + '-' + day[2] + '--' + g[1] + '-' + g[2]
      delivery = data['deliveries'][delivery_id] = {}
      delivery['time'] = str(datetime(*[int(x) for x in day], *[int(x) for x in g[1:]]))
      delivery['from'] = g[0]

    # linijka z zapłatą
    match = re.match('Base Payment PLN(.?.\...)$', line)
    if match:
      g = match.groups()
      delivery['payment'] = delivery['base_payment'] = float(g[0])
      print(delivery['payment'], end='')

    # linijka z odległością
    # może być np. "1.4 km" i "2.71 km"
    match = re.match('Distance Payment (.?.\..?.) km PLN(.?.\...)$', line)
    if match:
      g = match.groups()
      delivery['km'] = float(g[0])
      delivery['km_payment'] = float(g[1])
      delivery['payment'] += delivery['km_payment']
      print(delivery['payment'], end='')

    # linijka z napiwkiem
    match = re.match('Tip PLN(.?.\...)$', line)
    if match:
      g = match.groups()
      delivery['tip'] = float(g[0])
      delivery['payment'] += delivery['tip']
      print(delivery['payment'], end='')

    print()


data = read()
pp(data)

#s = ocr(*gl('S*')[2:4])
#deliveries(*s)
#s = read(*glob('S*'))

s = read_pages('delistare')

# sum([ data['deliveries'][y].get('km_payment',0) for y in data['deliveries'] ])
