from django.apps import AppConfig
from .model_services import ClassificationPredictor

class ClassifierConfig(AppConfig):
    name = 'classifier'
    predictor = ClassificationPredictor()

