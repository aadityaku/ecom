
from pyexpat import model
from django.core.exceptions import ObjectDoesNotExist
from re import template
from django.utils import timezone
from turtle import title
from unicodedata import category
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView,DetailView,View
from .models import Item, ItemVariation, OrderItem,Order,Variation,Category
# Create your views here.
class HomeView(ListView):
    model=Item
    template_name="index.html"
    
    def get_context_data(self):
        context=super(HomeView,self).get_context_data()
        context['categories'] = Category.objects.all()

        return context
class CategoryView(ListView):
    model=Item
    template_name="index.html"
    slug_url_kwarg="slug"
    def get_context_data(self,slug,*args,**kwargs):
        a=get_object_or_404(Category,title=slug)
       
        context=super(CategoryView,self).get_context_data(*args,**kwargs)
        #context['object_list']=Item.objects.filter(category=a)
        
        context['categories'] = Category.objects.all()

        return context
class ItemDetailsView(DetailView):
    model=Item
  
    template_name="product.html"
    slug_url_kwarg="slug"

    def get_context_data(self,*args,**kwargs):
        context=super(ItemDetailsView,self).get_context_data(*args,**kwargs)
        context['items'] = Item.objects.exclude(slug=self.kwargs['slug'])
        

        return context

class AddToCart(View):
    def get(self,request,slug,*args,**kwargs):
        item=get_object_or_404(Item,slug=slug)
        order_item,created=OrderItem.objects.get_or_create(item=item,user=request.user,ordered=False)
        var=[]
        varient=Variation.objects.filter(item=item)
        for v in varient:
            var.append(request.GET.get(v.name,None))
        order_qs = Order.objects.filter(user=request.user,ordered=False)

        if order_qs.exists():
            order = order_qs[0]
            if order.items.filter(user=request.user,ordered=False):
                order_item.qty +=1
                order_item.save()
                return redirect("core:order-summary")
                #not working
            else:
                order.items.add(order_item)
                for v in var:
                    a=ItemVariation.objects.get(value=v,variation__item__slug=item.slug)
                    
                    order_item.item_variations.add(a)
                    return redirect("core:order-summary")
        else:
            ordered_date=timezone.now()
            order=Order.objects.create(user=request.user,ordered_date=ordered_date)
            order.items.add(order_item)
            return redirect("core:order-summary")

class OrderSummary(View):
    def get(self,*args,**kwargs):
        try:
            order=Order.objects.get(user=self.request.user,ordered=False)
            context={"object":order}
        except ObjectDoesNotExist:
            return redirect("core:homepage")
        return render(self.request,"order-summary.html",context)
    
    model=Order
    template_name="order_summary.html"