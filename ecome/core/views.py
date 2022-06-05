

from multiprocessing import context
import random
import string

from django.conf import settings

from .forms import CouponForm,CheckoutForm
from pyexpat import model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from re import template
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import razorpay
from django.http import HttpResponseBadRequest
from unicodedata import category
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView,DetailView,View,UpdateView,CreateView
from .models import Address, Coupon, Item, ItemVariation, OrderItem,Order, Payment,Variation,Category
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages 
# Create your views here.
razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET)
)
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
                messages.success(request,"your quantity is updated sussecfully")
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
            messages.success(request,"your order is successfully")
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
            
class CheckoutView(View):

    def get(self,*args, **kwargs):
        address=Address.objects.filter(user=self.request.user)
        context={}
        try:
            order=Order.objects.get(user=self.request.user,ordered=False)
            form=CheckoutForm()
            amount = order.get_payable_amount() * 100
            currency = "INR"
            DATA = {
                "amount": amount,
                "currency": currency,
            }
            order_id = razorpay_client.order.create(data=DATA)

            context["order"] = order
            context["form"] = form
            context["address"] = address
            context["razorpay_key"] = settings.RAZOR_KEY_ID
            context["amount"] = order.get_payable_amount()
            context["order_id"] = order_id["id"]
            return render(
                self.request,
                "checkout.html",
                context=context,
            )
           

        except ObjectDoesNotExist:
            return redirect("core:checkout")
    def post(self,*args, **kwargs):
        if self.request.method == "POST":
            order=Order.objects.get(user=self.request.user,ordered=False)
            form=CheckoutForm(self.request.POST or None)
            #save_address=self.request.POST.get("save_address",None)
            
            if form.is_valid():
                data=form.save(commit=False)
                data.user=self.request.user
                data.save()
                order.address=data
                order.save()
                #makePayment(self,request)
                return redirect("core:checkout")
            else:
                return redirect("core:checkout")
        else:
            return redirect("core:checkout")

def save_Address_Action(r):
    form=CheckoutForm()
    address=Address.objects.filter(user=r.user)
    if r.method == "POST":
        order=Order.objects.get(user=r.user,ordered=False)
        save_address=r.POST.get("save_address",None)
        selected_address=Address.objects.get(id=save_address)
        order.address = selected_address

        order.save()
        #makePayment(r)
        return redirect("core:myorder")
@login_required
def myOrder(r):
    order=Order.objects.filter(user=r.user,ordered=True)
    return render(r,"myorder.html",{"order":order})   

def create_ref_code():
    return "".join(random.choices(string.ascii_lowercase + string.digits , k=20))

@csrf_exempt
def paymenthandler(request):

    # only accept POST request.
    if request.method == "POST":
        try:
            # print(request.POST.get("razorpay_payment_id"))
            # get the required parameters from post request.
            payment_id = request.POST.get("razorpay_payment_id", "")
            razorpay_order_id = request.POST.get("razorpay_order_id", "")
            signature = request.POST.get("razorpay_signature", "")
            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
            print(params_dict)

            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result is None:  # set None to True
                order = Order.objects.get(user=request.user, ordered=False)
                amount = order.get_payable_amount() * 100
                try:
                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)
                    payment = Payment()
                    payment.txt_id = "234565432345"
                    payment.user = request.user
                    payment.amount = order.get_payable_amount()

                    payment.save()

                    # assign the payment in order

                    order_item = order.items.all()
                    order_item.update(ordered=True)
                    order.ordered = True
                    order.payment = payment
                    order.ref_code = create_ref_code()
                    order.save()

                    # render success page on successful caputre of payment
                    return render(request, "paymentsuccess.html")

                except:

                    # if there is an error while capturing payment.
                    return render(request, "paymentfail.html")
            else:

                # if signature verification fails.
                return render(request, "paymentfail.html")
        except:

            # if we don't find the required parameters in POST data
            print("parameter issue")
            return HttpResponseBadRequest()
    else:
        print("post method issue")
        # if other than POST request is made.
        return HttpResponseBadRequest()


