import six
from six.moves.urllib import request as urllib2
from six.moves.urllib.parse import urlencode
from lxml import objectify, etree

STAT = {
	1:'успех',
	2:'доступ к расчету заблокирован',
	3:'неверные данные магазина (пароль или идентификатор)',
	4:'неверные входные параметры',
	5:'неверный город или страна',
	6:'внутренняя ошибка сервера расчетов',
	7:'не заданы компании доставки в настройках магазина',
	8:'сервер расчета не отвечает',
	9:'превышен лимит расчетов за день',
	11:'не указан вес',
	12:'не заданы данные магазина (пароль или идентификатор)',
}

class EdostXMLParseError(Exception):
	pass

class EdostClient(object):
	def __init__(self, client_id, password):
		self.client_id = client_id
		self.password = password
		pass

	def make_request(self, **kwargs):
		data = {
			'id': self.client_id,
			'p': self.password,
		}
		data.update(kwargs)
		if six.PY2:
			encoded_data = urlencode(data)
		else:
			encoded_data = urlencode(data).encode('cp1251')
		xml = urllib2.urlopen('http://www.edost.ru/edost_calc_kln.php', encoded_data).read()
		self._response = xml
		try:
			doc = objectify.fromstring(xml)
		except etree.XMLSyntaxError:
			raise EdostXMLParseError('There was a problem parsing the reply from Edost server. The response was {0!s}'.format(xml))

		self._parsed_response = doc
		return doc

	def get_tariffs(self, **kwargs):
		"""
		Fetch available tariffs. All keyword arguments will be sent to edost.ru.
		Advised arguments: to_city, weight, strah.
		"""
		doc = self.make_request(**kwargs)
		result = {}
		tarif = []
		try:
			for t in list(doc.tarif):
				tarif.append({
					'id': int(t.id),
					'company': six.u(t.company.text),
					'name': t.name.text and six.u(t.name.text) or None,
					'delivery_time': six.u(t.day.text),
					'price': float(t.price),
				})
		except AttributeError:
			self._delivery_only = tarif
		office = []
		try:
			for o in list(doc.office):
				office.append({
					'id': int(o.id),
					'to_tarif': [int(tarif) for tarif in o.to_tarif],
					'name': o.name.text and six.u(o.name.text) or None,
					'address': six.u(o.address.text),
					'tel': six.u(o.tel.text),
					'schedule': six.u(o.schedule.text),
					'gps': six.u(o.gps.text)
					})
		except AttributeError:
			self._pick_up_only = office
		stat = STAT[doc.stat]
		result.update({'tarif':tarif,'office':office})
		result.update({'stat':stat})
		self._parsed_response = result
		return result

	@property
	def parsed_response(self):
		assert hasattr(self,'_parsed_response'), 'Call get_tariffs first.'
		return self._parsed_response
	
	@property
	def pick_up_only(self):
		assert hasattr(self,'_parsed_response'), 'Call get_tariffs first.'
		if hasattr(self,'_pick_up_only'):
			return self._pick_up_only
		else:
			result_list = []
			for office in self._parsed_response.get('office'):
				for tarif in office.get('to_tarif'):
					found = False
					for item in result_list:
						if item.get('id') == tarif:
							item.get('addresses').append(office)
							found = True
					if not found:
						for tarif_details in self._parsed_response.get('tarif'):
							if tarif_details.get('id') == tarif:
								new_instance = tarif_details.copy()
								new_instance['addresses'] = [office]
								result_list.append(new_instance)
			self._pick_up_only = result_list
			return result_list

	@property
	def delivery_only(self):
		assert hasattr(self,'_parsed_response'), 'Call get_tariffs first.'
		if hasattr(self,'_delivery_only'):
			return self._delivery_only
		else:
			to_remove = []
			delivery_only = self._parsed_response.get('tarif').copy()
			for tarif in delivery_only:
				for office in self._parsed_response.get('office'):
					for office_tarif in office.get('to_tarif'):
						if office_tarif == tarif.get('id'):
							if not delivery_only.index(tarif) in to_remove:
								to_remove.append(delivery_only.index(tarif))
			to_remove.reverse()
			for remove in to_remove:
				delivery_only.pop(remove)
			self._delivery_only = delivery_only
			return delivery_only
