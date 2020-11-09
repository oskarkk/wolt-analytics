#!/usr/bin/python3 -i

import re
from datetime import datetime, date
from utils import *
#from pathlib import Path

def payouts(page):
  for line in page.splitlines():
    match = re.match('(.*)/(.*)/(.*) PLN (.*) >', line)
    if match:
      parts = match.groups()

      pyear = int(parts[2])
      pmonth = int(parts[1])
      phalf = int(parts[0])

      year = pyear

      if phalf == 1:
        half = 16
        if pmonth == 1:
          month = 12
          year = pyear-1
        else:
          month = pmonth-1
      elif phalf == 16:
        half = 1
        month = pmonth

      name = str(date(year, month, half))
      payout = data['payouts'].setdefault(name, {})
      payout['start'] = str(datetime(year, month, half))
      payout['end'] = str(datetime(pyear, pmonth, phalf))
      payout['value'] = float(parts[3].replace(',', ''))

def deliveries(*pages):
  data.setdefault('deliveries', {})
  s = []
  for page in pages:
    #page = page.replace('PLNO', 'PLN0')
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
    match = re.match('Base Payment PLN (.?.\...)$', line)
    if match:
      g = match.groups()
      delivery['payment'] = delivery['base_payment'] = float(g[0])
      print(delivery['payment'], end='')

    # linijka z odległością
    # może być np. "1.4 km" i "2.71 km"
    match = re.match('Distance Payment (.?.\..?.) km PLN (.?.\...)$', line)
    if match:
      g = match.groups()
      delivery['km'] = float(g[0])
      delivery['km_payment'] = float(g[1])
      delivery['payment'] += delivery['km_payment']
      print(delivery['payment'], end='')

    # linijka z napiwkiem
    match = re.match('Tip PLN (.?.\...)$', line)
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

s = read_pages('10-h2')

# sum([ data['deliveries'][y].get('km_payment',0) for y in data['deliveries'] ])
