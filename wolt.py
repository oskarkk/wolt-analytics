import re
import datetime as dt
dt.dt = dt.datetime
from utils import *
from collections import Counter

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

      name = str(dt.date(year, month, half))
      payout = data['payouts'].setdefault(name, {})
      payout['start'] = str(dt.dt(year, month, half))
      payout['end'] = str(dt.dt(pyear, pmonth, phalf))
      payout['value'] = float(parts[3].replace(',', ''))
      payout['deliveries'] = {}

def deliveries(*pages):
  data.setdefault('deliveries', {})
  s = ''.join(pages)
  
  patterns = {
    name: re.compile(pattern) for name, pattern in zip([
      'date', 'placetime', 'payment', 'distance', 'tip'
    ], [
      '\n(..)/(..)/(....)\n',
      '\n(.*) (..):(..)\n',
      'Base Payment PLN (.?.\...)$',
      'Distance Payment (.?.\..?.) km PLN (.?.\...)$',
      'Tip PLN (.?.\...)$'
    ])
  }

  details = {
    'payment': lambda g: {'base_payment': float(g[0])},
    'distance': lambda g: {'km': float(g[0]), 'km_payment': float(g[1])},
    'tip': lambda g: {'tip': float(g[0])}
  }

  def match(line, f):
    if m := patterns[f].match(line):
      g = m.groups()
      return details[f](g)
    return False

  def delivery(lines, place, time):
    datetime = dt.dt.combine(date, time)
    delivery = {
      'from': place,
      'payment': 0
    }

    details = ['payment', 'distance', 'tip']
    while lines and details:
      if d := match(lines.pop(0), details[0]):
        delivery.update(d)
        details.pop(0)

    # zapłata całkowita
    for x in ['base_payment', 'km_payment', 'tip']:
      delivery['payment'] += delivery.get(x, 0)
    # data + czas = id zamówienia
    return {str(datetime): delivery}

  def day(s):
    parts = patterns['placetime'].split(s)
    parts.pop(0)
    while parts:
      time = dt.time(int(parts[1]), int(parts[2]))
      place = parts[0]
      d = delivery(parts[3].splitlines(), place, time)
      data['deliveries'].update(d)
      del parts[:4]
  
  parts = re.split(patterns['date'], s)
  parts.pop(0)
  while parts:
    date = dt.date(int(parts[2]), int(parts[1]), int(parts[0]))
    day(parts[3])
    del parts[:4]

def deliveries_summary(deliveries):
  c = Counter()

  for delivery in deliveries.values():
    c.update(delivery)

  del c['from']
  c = dict(c)
  for num in c:
    c[num] = round(c[num], 2)
  return c


data = read()
pp(data)

#s = ocr(*gl('S*')[2:4])
#deliveries(*s)
#s = read(*glob('S*'))

s = read_pages('10-h2')
