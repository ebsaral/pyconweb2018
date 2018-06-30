from django.db import models

class Document(models.Model):
    name = models.TextField('Name')
    url = models.TextField('URL')
    create_date = models.DateTimeField(auto_now_add=True)


class Data(models.Model):
    client = models.CharField(max_length=255)
    time = models.DateTimeField()
    value = models.FloatField()
    create_date = models.DateTimeField(auto_now_add=True)