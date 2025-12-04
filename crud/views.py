from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import ListView,DetailView
from .models import Restaurant,Category
from django.contrib.auth import authenticate,login,logout
from .forms import SignupForm,LoginForm,ReviewForm,ReservationForm,SearchForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q

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

  def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant = self.get_object()

        context['reviews'] = restaurant.reviews.all()
        context['form'] = ReviewForm()
        return context

def category(request,category_id):
  category=get_object_or_404(Category,id=category_id)
  restaurants=category.restaurants.all()
  return render(request,'category_detail.html',{
    'category':category,
    'restaurants':restaurants,
  })

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('/')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def restaurant_review(request,restaurant_id):
     restaurant=get_object_or_404(Restaurant,id=restaurant_id)
     reviews=restaurant.reviews.all()

     if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.restaurant = restaurant
            review.user = request.user
            review.save()
            return redirect('restaurant_detail', restaurant_id=restaurant.id)
     else:
        form = ReviewForm()

     return render(request, 'restaurant_detail.html', {
        'restaurant': restaurant,
        'reviews': reviews,
        'form': form,
    })

@login_required
def reservation(request,restaurant_id):
    restaurant=get_object_or_404(Restaurant,id=restaurant_id)

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.restaurant=restaurant #自動的に店舗を紐づけ
            reservation.save()
            return redirect('reservation_success')
    else:
        form = ReservationForm()
    return render(request, 'reservation.html', {'form': form,'restaurant':restaurant})

def reservation_success(request):
    return render(request, 'reservation_success.html')

def search_view(request):
    form = SearchForm(request.GET or None)
    query = ''
    results = Restaurant.objects.none()

    if form.is_valid():
        query = form.cleaned_data['query']
        results = Restaurant.objects.filter(
            Q(name__icontains=query)|
            Q(category__name__icontains=query)
        )

    return render(request, 'search.html', {
        'form': form,
        'query': query,
        'results': results,
    })