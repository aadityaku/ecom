from .forms import CouponForm
from pyexpat import model

from django.core.exceptions import ObjectDoesNotExist
from re import template
from django.utils import timezone
from turtle import title
from unicodedata import category
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView,DetailView,View,UpdateView
from .models import Coupon, Item, ItemVariation, OrderItem,Order,Variation,Category
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
class HomeView(ListView):
    model=Item
    template_name="index.html"
    
    def get_context_data(self):
        context=super(HomeView,self).get_context_data()
        context['categories'] = Category.objects.all()
        context['count']=OrderItem.objects.filter(ordered=False).count()
        return context
#not working
def CategoryView(request,slug):
    a=Category.objects.get(pk=slug)
    
    context={"object_list":Item.objects.filter(category=a)}
    
    context= {"categories":Category.objects.all()}

    return render(request,"index.html",context)
class ItemDetailsView(DetailView):
    model=Item
  
    template_name="product.html"
    slug_url_kwarg="slug"

    def get_context_data(self,*args,**kwargs):
        context=super(ItemDetailsView,self).get_context_data(*args,**kwargs)
        context['items'] = Item.objects.exclude(slug=self.kwargs['slug'])
        #context['count']=OrderItem.objects.filter(user=self.request.user,ordered=False).count()

        return context

class AddToCart(LoginRequiredMixin,View):
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
            if order.items.filter(item__slug=item.slug).exists():
                order_item.qty +=1
                order_item.save()
                return redirect("core:order-summary")
                
            else:
                order.items.add(order_item)
                
                for v in var:
                    a=ItemVariation.objects.get(value=v,variation__item__slug=item.slug)
                    
                    order_item.item_variations.add(a)
                    
                return redirect("core:order-summary")
        else:
            ordered_date=timezone.now()
            order=Order.objects.create(user=request.user,start_date=ordered_date)
            order.items.add(order_item)
            return redirect("core:order-summary")

class OrderSummary(LoginRequiredMixin,View):
    def get(self,*args,**kwargs):
        try:
            order=Order.objects.get(user=self.request.user,ordered=False)
            if order.items.count()<1:
                return redirect("core:homepage")
            context={"object":order,"couponform":CouponForm()}
            #print(context)
        except ObjectDoesNotExist:
            return redirect("core:homepage")
        
        return render(self.request,"order-summary.html",context)
    
    model=Order
    template_name="order_summary.html"
#class RemoveFromCart(LoginRequiredMixin,View):
    #def get(self,request,slug,*args,**kwargs):
        #item=get_object_or_404(Item,slug=slug)
        #order_item=OrderItem.objects.get(item=item,user=request.user,ordered=False)
        #order_qs=Order.objects.filter(user=request.user,ordered=False,items=order_item)

        #if order_qs.exists():
            #order=order_qs[0]
            #if order.items.filter(item__slug=item.slug):
                #order_item.qty -=1
                #order_item.save()
                #return redirect("core:order-summary")
            #else:
                #return redirect("core:order-summary")
        #else:
            #return redirect("core:order-summary")
class RemoveFromCart(LoginRequiredMixin,View):
    def get(self,request,slug,*args,**kwargs):
        item=get_object_or_404(Item,slug=slug)
        order_qs=Order.objects.filter(user=request.user,ordered=False)
        
        if order_qs.exists():
            order = order_qs[0]
            if order.items.filter(item__slug=item.slug).exists():
                order_item=OrderItem.objects.filter(item=item,user=request.user,ordered=False)[0]
                order.items.remove(order_item)
                order_item.delete()
                return redirect("core:order-summary")
                
            else:
                return redirect("core:order-summary")
        else:
            return redirect("core:order-summary")
    
#def RemoveItem(request,slug):
    #item=get_object_or_404(Item,slug=slug)
    #order_item=OrderItem.objects.get(item=item,user=request.user,ordered=False)
    #order_qs=Order.objects.filter(user=request.user,ordered=False,items=order_item)
    #if order_qs.exists():
        #order=order_qs[0]
        #if order.items.filter(item__slug=item.slug):
            #order_item.delete()
            
            #return redirect("core:order-summary")
        #else:
            #return redirect("core:order-summary")
    #else:
        #return redirect("core:order-summary")
class MinusItemCart(LoginRequiredMixin,View):
    def get(self,request,slug,*args,**kwargs):
        item=get_object_or_404(Item,slug=slug)
        order_item,created=OrderItem.objects.get_or_create(user=request.user,ordered=False,item=item)
        #for varient
        var=[]
        varient=Variation.objects.filter(item=item)
        for v in varient:
            var.append(request.GET.get(v.name,None))
        order_qs=Order.objects.filter(user=request.user,ordered=False)
        if order_qs.exists():
            order=order_qs[0]
            if order.items.filter(item__slug=item.slug).exists():
                if order_item.qty > 1:
                    order_item.qty -=1
                    order_item.save()
                else:
                    order_item.delete()
                return redirect("core:order-summary")
        else:
            return redirect("core:order-summary")
def check_coupon(request,code):
    try:
        code=Coupon.objects.get(code=code)
        return True
    except ObjectDoesNotExist:
        return False

def get_coupon(request,code):
    try:
        coupon=Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        return redirect("core:order-summary")


class AddCoupon(View):
    def post(self,*args,**kwargs):
        if self.request.method == "POST":
            form=CouponForm(self.request.POST or None)
            if form.is_valid():
                try:
                    code=form.cleaned_data.get("code")
                    if check_coupon(self.request,code):
                        order=Order.objects.get(user=self.request.user,ordered=False)
                        order.coupon = get_coupon(self.request,code)
                        order.save()
                        return redirect("core:order-summary")
                    else:
                        return redirect("core:order-summary")
                except ObjectDoesNotExist:
                    return redirect("core:order-summary")


class RemoveCoupon(View):
    def get(self,*args,**kwargs):
        order=Order.objects.get(user=self.request.user,ordered=False)
        order.coupon = None
        order.save()
        return redirect("core:order-summary")
            
            
        






