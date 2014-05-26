from django.test import TestCase
from models import Content

import datetime

class ContentTestCase(TestCase):

	def setUp(self):
		Content.objects.create(title="Test1", date_modified=datetime.date.today())
