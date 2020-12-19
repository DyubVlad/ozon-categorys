from django.test import TestCase

from classifier.model_services import ClassificationPredictor


class ModelTestCase(TestCase):
    """Unit Tests для бизнес-логики приложеия Classifier"""

    def test_model_life(self):
        """Проверка метода модели возвращающего результат классификации"""
        """Проверяется факт ответа, а не точность"""
        testStr = 'Классификатор, ты живой?'
        model = ClassificationPredictor()
        result = str(model.getTextClass(testStr))
        self.assertTrue(result.isdigit())

    def test_punct_insign_func(self):
        """Проверка метода обработки текста, путём сравнения полученного ответа с ожидаемым"""
        inputStr = 'Моторное масло VAG (VW/Audi/Skoda/Seat) LONGLIFE III 0W-30 Синтетическое 1 л'
        outputStr = 'моторное масло vag audi skoda seat longlife iii синтетическое'
        model = ClassificationPredictor()
        result = str(model.delPunctuationAndInsig(inputStr))
        self.assertEqual(result, outputStr)
