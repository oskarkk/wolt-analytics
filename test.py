import re
import datetime as dt
dt.dt = dt.datetime
from utils import *
from collections import Counter

from timeit import timeit
from wolt import data, deliveries, deliveries_summary


s = read_pages('10-h2')
setup = 'from test import deliveries, deliveries2, deliveries3, deliveries4'

def test(f=deliveries):
  data['deliveries'] = {}
  print(timeit(lambda: f(*s[2:4], s[5]), setup=setup, number=1000))
  f()
  print(deliveries_summary(data['deliveries']))

# wersja z re.split w ciele i re.compile
def deliveries2(*pages):
  data.setdefault('deliveries', {})
  s = ''.join(pages)

  def m_date(g):
    return dt.date(int(g[2]), int(g[1]), int(g[0]))

  def m_placetime(g):
    return g[0], dt.time(int(g[1]), int(g[2]))

  def m_payment(g):
    return {'base_payment': float(g[0])}

  def m_distance(g):
    return {'km': float(g[0]), 'km_payment': float(g[1])}

  def m_tip(g):
    return {'tip': float(g[0])}
  
  pattern = dict(zip([
      m_date, m_placetime, m_payment, m_distance, m_tip
    ], [
      re.compile(x) for x in [
        '(..)/(..)/(....)\n',
        '(.*) (..):(..)$',
        'Base Payment PLN (.?.\...)$',
        'Distance Payment (.?.\..?.) km PLN (.?.\...)$',
        'Tip PLN (.?.\...)$'
      ]
    ]
  ))

  def match(line, f):
    if m := pattern[f].match(line):
      g = m.groups()
      return f(g)
    return False

  def delivery(lines, place, time):
    datetime = dt.dt.combine(date, time)
    delivery = {
      'from': place,
      'payment': 0
    }

    details = [m_payment, m_distance, m_tip]
    while lines and details:
      if d := match(lines.pop(0), details[0]):
        delivery.update(d)
        details.pop(0)

    # zapłata całkowita
    for x in ['base_payment', 'km_payment', 'tip']:
      delivery['payment'] += delivery.get(x, 0)
    # data + czas = id zamówienia
    return {str(datetime): delivery}

  def day(lines):
    while lines:
      # bierz linie dopóki nie będzie linii z czasem
      if placetime := match(lines.pop(0), m_placetime):
        delivery_lines = []
        while lines and not match(lines[0], m_placetime):
          # dodawaj linie do linii zamówienia dopóki nie będzie linii z czasem następnego zamówienia
          delivery_lines.append(lines.pop(0))
        # wyciągnij dane zamówienia
        d = delivery(delivery_lines, *placetime)
        data['deliveries'].update(d)
  
  #parts = pattern[m_date].split(pages)
  parts = re.split(pattern[m_date], s)
  parts.pop(0)
  #days = {}
  while parts:
    parts[0:4]
    date = dt.date(int(parts[2]), int(parts[1]), int(parts[0]))
    day(parts[3].splitlines())
    del parts[:4]

# wersja z re.split w ciele bez re.compile
def deliveries3(*pages):
  data.setdefault('deliveries', {})
  pages = ''.join(pages)

  def m_date(g):
    return dt.date(int(g[2]), int(g[1]), int(g[0]))

  def m_placetime(g):
    return g[0], dt.time(int(g[1]), int(g[2]))

  def m_payment(g):
    return {'base_payment': float(g[0])}

  def m_distance(g):
    return {'km': float(g[0]), 'km_payment': float(g[1])}

  def m_tip(g):
    return {'tip': float(g[0])}

  pattern = dict(zip([
      m_date, m_placetime, m_payment, m_distance, m_tip
    ], [
        '(..)/(..)/(....)\n',
        '(.*) (..):(..)$',
        'Base Payment PLN (.?.\...)$',
        'Distance Payment (.?.\..?.) km PLN (.?.\...)$',
        'Tip PLN (.?.\...)$'
    ]
  ))

  def match(line, f):
    if m := re.match(pattern[f], line):
      g = m.groups()
      return f(g)
    return False

  def delivery(lines, place, time):
    datetime = dt.dt.combine(date, time)
    delivery = {
      'from': place,
      'payment': 0
    }

    details = [m_payment, m_distance, m_tip]
    while lines and details:
      if d := match(lines.pop(0), details[0]):
        delivery.update(d)
        details.pop(0)

    # zapłata całkowita
    for x in ['base_payment', 'km_payment', 'tip']:
      delivery['payment'] += delivery.get(x, 0)
    # data + czas = id zamówienia
    return {str(datetime): delivery}

  def day(lines):
    while lines:
      # bierz linie dopóki nie będzie linii z czasem
      if placetime := match(lines.pop(0), m_placetime):
        delivery_lines = []
        while lines and not match(lines[0], m_placetime):
          # dodawaj linie do linii zamówienia dopóki nie będzie linii z czasem następnego zamówienia
          delivery_lines.append(lines.pop(0))
        # wyciągnij dane zamówienia
        d = delivery(delivery_lines, *placetime)
        data['deliveries'].update(d)
  
  #parts = pattern[m_date].split(pages)
  parts = re.split(pattern[m_date], pages)
  parts.pop(0)
  #days = {}
  while parts:
    parts[0:4]
    date = dt.date(int(parts[2]), int(parts[1]), int(parts[0]))
    day(parts[3].splitlines())
    del parts[:4]

# wersja z pętlami while i re.compile
def deliveries4(*pages):
  data.setdefault('deliveries', {})
  s = []
  for page in pages:
    s += page.splitlines()

  def m_date(g):
    return dt.date(int(g[2]), int(g[1]), int(g[0]))

  def m_placetime(g):
    return g[0], dt.time(int(g[1]), int(g[2]))

  def m_payment(g):
    return {'base_payment': float(g[0])}

  def m_distance(g):
    return {'km': float(g[0]), 'km_payment': float(g[1])}

  def m_tip(g):
    return {'tip': float(g[0])}

  pattern = dict(zip([
      m_date, m_placetime, m_payment, m_distance, m_tip
    ], [
      re.compile(x) for x in [
        '(..)/(..)/(....)$',
        '(.*) (..):(..)$',
        'Base Payment PLN (.?.\...)$',
        'Distance Payment (.?.\..?.) km PLN (.?.\...)$',
        'Tip PLN (.?.\...)$'
      ]
    ]
  ))

  def match(line, f):
    if m := pattern[f].match(line):
      g = m.groups()
      return f(g)
    return False

  def delivery(lines, place, time):
    datetime = dt.dt.combine(date, time)
    delivery = {
      'from': place,
      'payment': 0
    }

    details = [m_payment, m_distance, m_tip]
    while lines and details:
      if d := match(lines.pop(0), details[0]):
        delivery.update(d)
        details.pop(0)

    # zapłata całkowita
    for x in ['base_payment', 'km_payment', 'tip']:
      delivery['payment'] += delivery.get(x, 0)
    # data + czas = id zamówienia
    return {str(datetime): delivery}

  def day(lines):
    while lines:
      # bierz linie dopóki nie będzie linii z czasem
      if placetime := match(lines.pop(0), m_placetime):
        delivery_lines = []
        while lines and not match(lines[0], m_placetime):
          # dodawaj linie do linii zamówienia dopóki nie będzie linii z czasem następnego zamówienia
          delivery_lines.append(lines.pop(0))
        # wyciągnij dane zamówienia
        d = delivery(delivery_lines, *placetime)
        data['deliveries'].update(d)

  # przetwarzanie wszystkich linii
  while s:
    # bierz linie dopóki nie będzie linii z datą
    if date := match(s.pop(0), m_date):
      day_lines = []
      while s and not match(s[0], m_date):
        # dodawaj następne linie do day_lines dopóki nie będzie następnej linii z datą
        day_lines.append(s.pop(0))
      # znajdź zamówienia w liniach danego dnia
      day(day_lines)

# wersja przejściowa niedziałająca z pętlami while, bez re.compile, bez match()
def deliveries5(*pages):
  data.setdefault('deliveries', {})
  s = []
  for page in pages:
    #page = page.replace('PLNO', 'PLN0')
    s += page.splitlines()

  exp = dict(zip([
      'date', 'time', 'payment', 'distance', 'tip'
    ], [
      '(..)/(..)/(....)$',
      '(.*) (..):(..)$',
      'Base Payment PLN (.?.\...)$',
      'Distance Payment (.?.\..?.) km PLN (.?.\...)$',
      'Tip PLN (.?.\...)$'
    ]
  ))

  def line_day(line):
    if match := re.match(exp['date'], line):
      return [int(x) for x in match.groups()[::-1]]
    else:
      return False

  def line_time(line):
    if match := re.match(exp['time'], line):
      g = match.groups()
      return [g[0]] + [int(x) for x in g[1:]]
    else:
      return False

  def line_payment(line):
    if match := re.match(exp['payment'], line):
      g = match.groups()
      d = {'base_payment': float(g[0])}
      return d
    else:
      return False

  def line_distance(line):
    if match := re.match(exp['distance'], line):
      g = match.groups()
      d = {}
      d['km'] = float(g[0])
      d['km_payment'] = float(g[1])
      return d
    else:
      return False

  def line_tip(line):
    if match := re.match(exp['tip'], line):
      g = match.groups()
      d = {'tip': float(g[0])}
      return d
    else:
      return False

  def delivery():
    if placetime := line_time(s[0]):
      s.pop(0)
      time = dt.dt(*day, *placetime[1:])
      delivery = {
        'from': placetime[0],
        'payment': 0
      }
      for f in [line_payment, line_distance, line_tip]:
        if d := f(s[0]):
          delivery.update(d)
          s.pop(0)
      for x in ['base_payment', 'km_payment', 'tip']:
        delivery['payment'] += delivery.get(x, 0)
      d = {str(time): delivery}
      data['deliveries'].update(d)
    else:
      return False

  while s:

    if is_day := line_day(s.pop(0)):
    #if is_day := line_day(s[0]):
      day = is_day
      if d := delivery():
        pass

    else:
      if not s:
        break
      if d := delivery():
        pass

# wersja pierwotna z wielkim forem bez re.compile
def deliveries6(*pages):
  data.setdefault('deliveries', {})
  s = []
  for page in pages:
    #page = page.replace('PLNO', 'PLN0')
    s += page.splitlines()
  day = None
  delivery = None
  for line in s:

    #print(line.ljust(40), end='')

    # linijka z datą (data przypisywana do wszystkich zamówień aż do znalezienia nast. daty)
    match = re.match('(..)/(..)/(....)$', line)
    if match:
      day = match.groups()[::-1]

    # linijka z restauracją i czasem (data + czas = id zamówienia)
    match = re.match('(.*) (..):(..)$', line)
    if match:
      g = match.groups()
      time = dt.dt(*[int(x) for x in day + g[1:]])
      delivery = data['deliveries'][str(time)] = {}
      delivery['from'] = g[0]
      # add deliveries to payouts
      for payout in data['payouts'].values():
        start = dt.dt.fromisoformat(payout['start'])
        end = dt.dt.fromisoformat(payout['end'])
        if time > start and time < end:
          payout['deliveries'][str(time)] = delivery
          break

    # linijka z zapłatą
    match = re.match('Base Payment PLN (.?.\...)$', line)
    if match:
      g = match.groups()
      delivery['payment'] = delivery['base_payment'] = float(g[0])
      #print(delivery['payment'], end='')

    # linijka z odległością
    # może być np. "1.4 km" i "2.71 km"
    match = re.match('Distance Payment (.?.\..?.) km PLN (.?.\...)$', line)
    if match:
      g = match.groups()
      delivery['km'] = float(g[0])
      delivery['km_payment'] = float(g[1])
      delivery['payment'] += delivery['km_payment']
      #print(delivery['payment'], end='')

    # linijka z napiwkiem
    match = re.match('Tip PLN (.?.\...)$', line)
    if match:
      g = match.groups()
      delivery['tip'] = float(g[0])
      delivery['payment'] += delivery['tip']
      #print(delivery['payment'], end='')

    #print()