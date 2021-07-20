from django.shortcuts import render
from core.models import Item


def item_list(request):
    item_objects = Item.objects.all()
    context = {
        'items': item_objects
    }
    return render(request, "product-page.html", context=context)

def checkout(request):
    return render(request, 'chekout-page.html')

def home(request):
    item_objects = Item.objects.all()
    context = {
        'items': item_objects
    }
    return render(request, 'home-page.html', context=context)