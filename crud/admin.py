from django.contrib import admin
from .models import Restaurant,Category,Review
from django.utils.safestring import mark_safe

# Register your models here.
class RestaurantAdmin(admin.ModelAdmin):
  list_display=('id','name','price','address','image','category')
  search_fields=('name',)
  list_filter=('category',)

  def image(self,obj):
    return mark_safe('<img src="{}" style="width:100px height:auto;">'.format(obj.img.url))

class CategoryAdmin(admin.ModelAdmin):
  list_display=('id','name')
  search_fields=('name',)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'user', 'rating', 'comment', 'created_at')
    list_filter = ('restaurant', 'rating', 'created_at')
    search_fields = ('user__username', 'comment')


admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Review,ReviewAdmin)

