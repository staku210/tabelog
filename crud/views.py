from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import ListView,DetailView
from .models import Restaurant,Category,Favorite,Reservation
from django.contrib.auth import authenticate,login,logout
from .forms import SignupForm,LoginForm,ReviewForm,ReservationForm,SearchForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q

# Create your views here.
class RestaurantListView(ListView):
  model=Restaurant
  template_name = "restaurant_list.html"

  def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            # 各レストランに `is_favorited` フラグを追加
            favorites = Favorite.objects.filter(user=self.request.user).values_list('restaurant_id', flat=True)
            for restaurant in queryset:
                restaurant.is_favorited = restaurant.id in favorites
        return queryset

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


@login_required
def toggle_favorite(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, restaurant=restaurant)

    if not created:
        favorite.delete()  # 登録済みなら解除
    return redirect('list')


@login_required
def account_view(request):
    user=request.user
    favorite=Favorite.objects.filter(user=user).select_related('restaurant')
    reservation=Reservation.objects.filter(user=user).select_related('restaurant')
    return render(request, 'account.html', {
        'user': user,
        'favorites': favorite,
        'reservations': reservation,
    })