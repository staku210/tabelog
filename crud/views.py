import json
import stripe
from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import ListView,DetailView,DeleteView,UpdateView
from .models import Restaurant,Category,Favorite,Reservation,Review
from django.contrib.auth import authenticate,login,logout,update_session_auth_hash,get_user_model
from .forms import SignupForm,LoginForm,ReviewForm,ReservationForm,SearchForm,UserEditForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib.auth.forms import PasswordChangeForm
from .forms import ReviewForm
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

stripe.api_key=settings.STRIPE_SECRET_KEY

User=get_user_model()

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
def user_edit_view(request):
    if request.method=='POST':
        form=UserEditForm(request.POST,instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('account')
    else:
        form=UserEditForm(instance=request.user)
    return render(request,'user_edit.html',{'form':form})

@login_required
def password_reset_view(request):
    if request.method=='POST':
        form=PasswordChangeForm(user=request.user,data=request.POST)
        if form.is_valid():
            user=form.save()
            update_session_auth_hash(request,user) #ログアウトされないようにする
            return redirect('account')
    else:
            form=PasswordChangeForm(user=request.user)
    return render(request,'password_reset.html',{'form':form})


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
            return redirect('detail', pk=restaurant.pk)
     else:
        form = ReviewForm()

     return render(request, 'restaurant_detail.html', {
        'restaurant': restaurant,
        'reviews': reviews,
        'form': form,
    })


class ReviewUpdateView(UpdateView):
    model=Review
    form_class=ReviewForm
    template_name="review_update_form.html"

    def get_success_url(self):
        return reverse_lazy('detail',kwargs={'pk':self.object.restaurant.id})
    
    def get_queryset(self):
        #ログインユーザーのレビューのみ編集可能にする
        qs=super().get_queryset()
        return qs.filter(user=self.request.user)

class ReviewDeleteView(DeleteView):
    model=Review
    template_name="review_delete.html"

    def get_success_url(self):
        return reverse_lazy('detail',kwargs={'pk':self.object.restaurant.id})
    
    def get_queryset(self):
        qs=super().get_queryset()
        return qs.filter(user=self.request.user)


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

class ReservationDeleteView(DeleteView):
    model=Reservation
    template_name='reservation_delete.html'
    success_url=reverse_lazy('account') #キャンセル後にアカウントページに戻る

    def get_queryset(self):
        #自分の予約しか削除できないようにする
        return Reservation.objects.filter(user=self.request.user)


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
    favorites=Favorite.objects.filter(user=user).select_related('restaurant')
    reservation=Reservation.objects.filter(user=user).select_related('restaurant')
    return render(request, 'account.html', {
        'user': user,
        'favorites': favorites,
        'reservations': reservation,
    })


#stripe checkoutセッションを作成
@login_required
def create_checkout_session(request):

    checkout_session = stripe.checkout.Session.create(
        customer_email=request.user.email,  # Stripeに顧客を自動作成
        payment_method_types=['card'],
        line_items=[
            {
                'price': settings.STRIPE_PRICE_ID,
                'quantity': 1,
            },
        ],
        mode='subscription',
        success_url=YOUR_DOMAIN + '/success/',
        cancel_url=YOUR_DOMAIN + '/cancel/',
    )
    return redirect(checkout_session.url)

def success(request):
    return render(request,'success.html')

def cancel(request):
    return render(request,'cancel.html')


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    print(f"✅ 受信イベントタイプ: {event['type']}")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session.get("customer_email")
        stripe_customer_id = session.get("customer")  # cus_XXXXXX

        try:
            user = User.objects.get(email=customer_email)
            user.is_premium = True
            user.stripe_customer_id = stripe_customer_id
            user.save()
            print(f"🎉 ユーザー {user.email} をプレミアムに更新しました")
        except User.DoesNotExist:
            print(f"⚠️ 該当ユーザーが見つかりません: {customer_email}")

    return HttpResponse(status=200)


@login_required
def cancel_subscription(request):
    user = request.user
    if user.stripe_customer_id:
        # 顧客のサブスクリプション一覧を取得
        subscriptions = stripe.Subscription.list(customer=user.stripe_customer_id)
        for sub in subscriptions.data:
            stripe.Subscription.delete(sub.id)  # サブスクリプションをキャンセル
        # Django 側のフラグを更新
        user.is_premium = False
        user.save()
    return redirect('account')  # アカウントページなどに戻る