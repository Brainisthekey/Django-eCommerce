from django.shortcuts import render
from core.models import Item


def item_list(request):
    item_objects = Item.objects.all()
    context = {
        'items': item_objects
    }
    return render(request, "home-page.html", context=context)