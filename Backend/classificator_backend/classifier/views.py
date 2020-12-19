from django.shortcuts import render
from .apps import ClassifierConfig
from rest_framework.views import APIView
from rest_framework.response import Response
from texts.texts_services import TextServices


def classifierApp(request):
    """Возвращает шаблон приложения клиенту"""
    return render(request, 'classifier_app.html')

class CallModel(APIView):
    """API endpoint /api/model/ для обработки запросов на определение класса для передаваемого текста"""

    def get(self, request):
        if request.method == 'GET':
            params = request.GET.get('text')
            if params:
                txtServObj = TextServices()
                response = ClassifierConfig.predictor.getTextClass(text=str(params))
                className = txtServObj.getClassNameById(classId=response)
                return Response(str(className))
            else:
                return Response(status=204)


