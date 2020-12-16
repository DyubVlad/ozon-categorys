from django.db import models


class Categorylist(models.Model):
    categoryid = models.AutoField(db_column='categoryId', primary_key=True)
    categoryname = models.TextField(db_column='categoryName', unique=True)

    def __str__(self):
        return self.categoryname


class Goods(models.Model):
    itemid = models.AutoField(db_column='itemId', primary_key=True)
    itemtitle = models.TextField(db_column='itemTitle')
    itemdescription = models.TextField(db_column='itemDescription')
    categoryid = models.ForeignKey(Categorylist, models.DO_NOTHING, db_column='categoryid')

    def __str__(self):
        return self.itemtitle

