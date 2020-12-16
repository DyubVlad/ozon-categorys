from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from texts.serializers import TextSerializer, ClassSerializer
from .texts_services import TextServices as ts, CustomPaginator
from rest_framework.response import Response

from django.http import HttpResponse, JsonResponse


class Texts(APIView):

    def get(self, request):
        if request.method == 'GET':
            method = request.GET.get('method')
            textsServices = ts()
            if method == 'getClasses':
                classes = textsServices.getClassList()
                serializer = ClassSerializer(classes, many=True)
                return Response(serializer.data)
            elif method == 'getAllTexts':
                texts = textsServices.getAllTexts()
                paginator = CustomPaginator()
                response = paginator.generate_response(texts, TextSerializer, request)
                return response
            elif method == 'getAllTextsByClass':
                category = request.GET.get('category')
                texts = textsServices.getAllTextsByClass(category)
                paginator = CustomPaginator()
                response = paginator.generate_response(texts, TextSerializer, request)
                return response

