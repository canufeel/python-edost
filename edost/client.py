import six
from six.moves.urllib import request as urllib2
from six.moves.urllib.parse import urlencode
import lxml

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
			doc = lxml.objectify.fromstring(xml)
		except lxml.etree.XMLSyntaxError:
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
		if hasattr(doc, 'tarif'):
			tarif = []
			for t in list(doc.tarif):
				options.append({
					'id': int(t.id),
					'company': six.u(t.company.text),
					'name': t.name.text and six.u(t.name.text) or None,
					'delivery_time': six.u(t.day.text),
					'price': float(t.price),
				})
			office = []
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
			result.update({'tarif':tarif,'office':office})
		stat = STAT[doc.stat]
		result.update({'stat':stat})
		return result