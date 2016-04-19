# python-edost

This is a simple set of Python bindings for edost.ru, a Russian delivery cost calculation service.

## Installation

    pip install edost

## Usage

Get the list of tariffs:

```python
import edost
	
edost_client = edost.EdostClient('<client id>', '<password>')
tariffs = edost_client.get_tariffs(
	to_city=edost.EDOST_ID_FOR_CITY[u'Сургут'],
	weight=1,
	strah=1000,
)

 # would show just tarifs
print tariffs['tarif'][0]  # {'company': 'Почта России','delivery_time': '8 дней','id': 1,'name': 'отправление 1-го класса','price': 213.58}

 # would show just offices
print tariffs['office'][0] 
 '''
 {'address': 'ул. Энергетиков, д. 20, оф. 112','gps': '73.401260,61.241743','id': 58,'name': 'ул. Энергетиков, д. 20','schedule': 'пн.-сб. с 09:00 до 18:00','tel': '8-800-700-54-30','to_tarif': [36]}
 '''

 #would filter out options related to office delivery and show only delivery to-door.
print edost_client.delivery_only[0] # {'company': 'Почта России','delivery_time': '8 дней','id': 1,'name': 'отправление 1-го класса','price': 213.58}
 
 '''
 would filter out options related to to-door delivery and show only options related to self pick-up and populate additional 'addresses' list for each one which is a list of pick-up addresses for this carrier.
 '''
print edost_client.delivery_only[0] 
 '''
 {'addresses': [{'address': 'ул. Энергетиков, д. 20, оф. 112',
   'gps': '73.401260,61.241743',
   'id': 58,
   'name': 'ул. Энергетиков, д. 20',
   'schedule': 'пн.-сб. с 09:00 до 18:00',
   'tel': '8-800-700-54-30',
   'to_tarif': [36]},
  {'address': 'проспект Ленина, д. 46',
   'gps': '73.389951,61.255233',
   'id': 5122,
   'name': 'проспект Ленина, д. 46',
   'schedule': 'пн.-пт. с 10:00 до 19:40, сб.-вс. с 11:00 до 18:40',
   'tel': '8-800-700-54-30',
   'to_tarif': [36]},
  {'address': 'Комсомольский проспект, д. 13',
   'gps': '73.439603,61.240145',
   'id': 6320,
   'name': 'Комсомольский проспект, д. 13',
   'schedule': 'пн.-пт. с 10:00 до 19:00',
   'tel': '8-800-700-54-30',
   'to_tarif': [36]}],
 'company': 'boxberry',
 'delivery_time': '7 дней',
 'id': 36,
 'name': 'до пункта выдачи',
 'price': 544.0}
 '''

```

Construct the city selector:

```python
import edost
from django.db import models

CITY_CHOICES = [(city_code, full_city) for city_code, city, region, full_city in edost.EDOST_CITIES]
city_code = models.PositiveIntegerField(choices=CITY_CHOICES)
```