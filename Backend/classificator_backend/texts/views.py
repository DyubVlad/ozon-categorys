from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from texts.serializers import TextSerializer, ClassSerializer
from .texts_services import TextServices as ts, CustomPaginator
from rest_framework.response import Response

from django.http import HttpResponse, JsonResponse


class Texts(APIView):
    """API endpoint /api/text/ для обработки запросов на получения информации о колекции текстов"""

    def get(self, request):
        if request.method == 'GET':
            method = request.GET.get('method')
            textsServices = ts()
            if method == 'getClasses':    # Возвращает список классов
                classes = textsServices.getClassList()
                serializer = ClassSerializer(classes, many=True)
                return Response(serializer.data)
            elif method == 'getAllTexts':    # Возвращает все объекты модели Goods разбитые на старницы
                texts = textsServices.getAllTexts()
                paginator = CustomPaginator()
                response = paginator.generate_response(texts, TextSerializer, request)
                return response
            elif method == 'getAllTextsByClass':    # Возвращает все объекты модели Goods с фильтром по классу
                category = request.GET.get('category')
                texts = textsServices.getAllTextsByClass(category)
                paginator = CustomPaginator()
                response = paginator.generate_response(texts, TextSerializer, request)
                return response

