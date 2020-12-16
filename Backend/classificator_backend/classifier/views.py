from django.shortcuts import render
from .apps import ClassifierConfig

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from texts.texts_services import getClassNameById


def classifierApp(request):
    return render(request, 'classifier_app.html')

class CallModel(APIView):

    def get(self, request):
        if request.method == 'GET':
            params = request.GET.get('text')
            if params:
                response = ClassifierConfig.predictor.getTextClass(text=str(params))
                className = getClassNameById(classId=response)
                return Response(str(className))
            else:
                return HttpResponse(status=204)


