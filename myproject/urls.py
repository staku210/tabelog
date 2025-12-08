"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from crud import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.RestaurantListView.as_view(),name="list"),
    path('detail/<int:pk>/',views.RestaurantDetailView.as_view(),name='detail'),
    path('category/<int:category_id>',views.category,name='category'),
    path('accounts/',include('crud.urls')),
    path('review/<int:restaurant_id>/', views.restaurant_review, name='review'),
    path('reservation/<int:restaurant_id>/',views.reservation,name='reservation'),
    path('reservation-success/',views.reservation_success,name='reservation_success'),
    path('search/',views.search_view,name='search'),
    path('favorite/<int:restaurant_id>/',views.toggle_favorite,name='favorite'),
    path('account/',views.account_view,name='account'),
    path('reservation/<int:pk>/delete/',views.ReservationDeleteView.as_view(),name="reservation_delete"),
    path('account/edit/',views.user_edit_view,name='user_edit'),
    path('account/password/',views.password_reset_view,name='password_reset'),
    path('reviews/<int:pk>/edit/',views.ReviewUpdateView.as_view(),name="review_update"),
    path('reviews/<int:pk>/delete/',views.ReviewDeleteView.as_view(),name="review_delete"),
    path('create-checkout-session/',views.create_checkout_session,name='create-checkout-session'),
    path('success/',views.success,name='success'),
    path('cancel/',views.cancel,name='cancel'),
    path('webhook/',views.stripe_webhook,name='stripe_webhook'),
    path('cancel-subscription/',views.cancel_subscription,name='cancel_subscription'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)