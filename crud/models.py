from django.db import models

# Create your models here.
class Category(models.Model):
  name=models.CharField(max_length=200)

  def __str__(self):
    return self.name

class Restaurant(models.Model):
  name=models.CharField(max_length=200)
  price=models.CharField(max_length=200)
  address=models.CharField(max_length=200)
  img=models.ImageField(blank=True,default='noImage.png')
  category=models.ForeignKey(Category,on_delete=models.CASCADE,related_name='restaurants')

  def __str__(self):
    return self.name