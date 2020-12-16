from rest_framework.serializers import ModelSerializer

from texts.models import Goods, Categorylist


class ClassSerializer(ModelSerializer):
    class Meta:
        model = Categorylist
        fields = ['categoryid', 'categoryname']

class TextSerializer(ModelSerializer):
    categoryid = ClassSerializer('categoryname', required=False)
    class Meta:
        model = Goods
        fields = ['itemtitle', 'itemdescription', 'categoryid']
