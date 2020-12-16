import re

testStr = ' Описание Автомобильные шины NEXEN CLASSE PREMIERE CP643a 225/55R17 97VПроизводитель: NEXENМодель:/' \
          ' CLASSE PREMIERE CP643AСезон: летоТипоразмер: 225/55R17Индекс скорости: VИндекс нагрузки: 97 '
#testStr = testStr.lower()
res = ''
testStr = re.match(r'\b[а-я]{1}[А-Я]{1}\b', testStr)
testStr = re.sub(r'[^\w\s]+|[\d]+|км/ч|\b\w{0,2}\b', res, testStr)
print(testStr)
testStr = re.sub(r'\b\w{0,2}\b', res, testStr).strip()
print(testStr)
print()