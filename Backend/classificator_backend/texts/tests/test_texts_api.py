from rest_framework import status
from rest_framework.test import APITestCase


class ModelApiTestCase(APITestCase):
    """Unit Tests для API приложения Texts"""
    fixtures = ['dump_cat.json', 'dump_goods.json']

    def test_get_classes(self):
        """Проврка успешного ответа от endpoint, возврщающего список класов"""
        url = 'http://127.0.0.1:8000/api/texts/?method=getClasses'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_texts(self):
        """Проврка успешного ответа от endpoint, возврщающего список всех текстов"""
        url = 'http://127.0.0.1:8000/api/texts/?method=getAllTexts'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_texts_by_cat(self):
        """Проврка успешного ответа от endpoint, возврщающего список текстов для переданной в запросе категории"""
        category = '5'
        url = 'http://127.0.0.1:8000/api/texts/?method=getAllTextsByClass&category=' + category
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
