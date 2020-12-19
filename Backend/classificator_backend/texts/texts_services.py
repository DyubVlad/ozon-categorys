from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound as NotFoundError
from .models import Categorylist, Goods
from rest_framework.response import Response


class TextServices:

    def getClassList(self):
        """Возвращает полный список категорий из БД"""
        return Categorylist.objects.all()

    def getAllTexts(self):
        """Возвращает полный список объектов в таблице Goods - все товары в БД"""
        return Goods.objects.select_related()

    def getAllTextsByClass(self, category):
        """Возвращает все объекты из таблицы Goods для указанного id категории"""
        return Goods.objects.filter(categoryid=category)

    def getClassNameById(self, classId):
        """Возвращает название категории по её id"""
        className = Categorylist.objects.get(categoryid=classId)
        return className.categoryname


class CustomPaginator(PageNumberPagination):
    """Пагинатор из библиотеки DRF адаптированный для APIVew"""
    page_size = 10      # Кол-во объектов на одной странице

    def generate_response(self, query_set, serializer_obj, request):
        try:
            page_data = self.paginate_queryset(query_set, request)
        except NotFoundError:
            return Response({"error": "No results found for the requested page"}, status=status.HTTP_400_BAD_REQUEST)

        serialized_page = serializer_obj(page_data, many=True)
        return self.get_paginated_response(serialized_page.data)