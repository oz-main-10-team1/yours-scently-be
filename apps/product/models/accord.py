from django.db import models


class Accord(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class MainAccord(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name