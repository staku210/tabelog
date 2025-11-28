from django.contrib import admin
from .models import Restaurant
from django.utils.safestring import mark_safe

# Register your models here.
class RestaurantAdmin(admin.ModelAdmin):
  list_display=('id','name','price','address','image')
  search_fields=('name',)

  def image(self,obj):
    return mark_safe('<img src="{}" style="width:100px height:auto;">'.format(obj.img.url))


admin.site.register(Restaurant, RestaurantAdmin)

