from django.shortcuts import render,get_object_or_404
from django.views.generic import ListView,DetailView
from .models import Restaurant,Category

# Create your views here.
class RestaurantListView(ListView):
  model=Restaurant
  template_name = "restaurant_list.html"

  def get_context_data(self, **kwargs):
    context=super().get_context_data(**kwargs)
    context['categories'] = Category.objects.all()
    return context

class RestaurantDetailView(DetailView):
  model=Restaurant
  template_name="restaurant_detail.html"


def category(request,category_id):
  category=get_object_or_404(Category,id=category_id)
  restaurants=category.restaurants.all()
  return render(request,'category_detail.html',{
    'category':category,
    'restaurants':restaurants,
  })