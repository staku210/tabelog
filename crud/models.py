from django.db import models

# Create your models here.
class Restaurant(models.Model):
  name=models.CharField(max_length=200)
  price=models.CharField(max_length=200)
  address=models.CharField(max_length=200)
  img=models.ImageField(blank=True,default='noImage.png')

  def __str__(self):
    return self.name