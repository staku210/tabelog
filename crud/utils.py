from django.http import HttpResponseForbidden
from django.shortcuts import render

def premium_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_premium:
            return render(request,'premium_required.html',status=403)
        return view_func(request, *args, **kwargs)
    return wrapper