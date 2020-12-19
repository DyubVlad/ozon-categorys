from rest_framework import status
from rest_framework.test import APITestCase


class ModelApiTestCase(APITestCase):
    """Unit Tests для API endpoint классификатора"""
    fixtures = ['dump_cat.json']

    def test_get_class(self):
        """Проверка метода getTextClass, возвращающего результат классификации"""
        apiUrl = 'http://127.0.0.1:8000/api/model/?text='
        testTxt = 'диски'
        url = apiUrl + testTxt
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
