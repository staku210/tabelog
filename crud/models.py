from django.db import models
from django.contrib.auth.models import User

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

class Review(models.Model):
  restaurant=models.ForeignKey(Restaurant,on_delete=models.CASCADE,related_name='reviews')
  user=models.ForeignKey(User,on_delete=models.CASCADE)
  rating=models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)]) #1～5の評価
  comment=models.TextField()
  created_at=models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"{self.user.username} - {self.restaurant.name}"