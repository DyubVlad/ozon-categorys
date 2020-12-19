from django.test import TestCase
from texts.texts_services import TextServices


class TextsServicesTestCase(TestCase):
    """Unit Tests для бизнес-логики приложеия Texts"""
    fixtures = ['dump_cat.json', 'dump_goods_small.json']

    def setUp(self):
        self.testObject = TextServices()
        self.categoryCount = 9

        self.textCountInDumpSmall = 4

        self.testIdClass = 5
        self.checkClass = 'присадки'

        self.testIdForTexts = 3
        self.testTextsCoun = 2

    def test_getClassList(self):
        """Проверка метода, возвращающего список классов,"""
        """путем сравнения полченного и ожидаемого кол-ва элем-ов"""
        result = self.testObject.getClassList()
        self.assertEqual(len(result), self.categoryCount)

    def test_getAllTexts(self):
        """Проверка метода, возвращающего все обекты модели Goods,"""
        """путем сравнения полченного и ожидаемого кол-ва объектов тестового набора"""
        result = self.testObject.getAllTexts()
        self.assertEqual(len(result), self.textCountInDumpSmall)

    def test_getClassNameById(self):
        """Проверка метода, возвращающего имя класса по его id,"""
        """путем сравнения полченного и ожидаемого рзультата"""
        result = self.testObject.getClassNameById(self.testIdClass)
        self.assertEqual(result, self.checkClass)

    def test_getAllTextsByClass(self):
        """Проверка метода, возвращающего все объекты модели Goods с фильтром по id класса,"""
        """путем сравнения полченного и ожидаемого кол-ва объектов на тестовом наборе"""
        result = self.testObject.getAllTextsByClass(self.testIdForTexts)
        self.assertEqual(len(result), self.testTextsCoun)



