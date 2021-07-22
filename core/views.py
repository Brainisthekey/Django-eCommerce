from django.shortcuts import render
from django.views.generic.detail import DetailView
from core.models import Item
from django.views.generic import ListView, DeleteView


def checkout(request):
    return render(request, 'chekout-page.html')

class HomeView(ListView):
    
    model = Item
    template_name = 'home-page.html'
    context_object_name = 'items'

class ItemDetailView(DetailView):

    model = Item
    template_name = 'product-page.html'