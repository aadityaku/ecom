
from tabnanny import verbose
from django.conf import settings
from email.mime import image
from pyexpat import model
from tkinter.tix import Balloon
from django.urls import reverse
from pydoc import describe
from django.db import models

class Category(models.Model):
    title=models.CharField(max_length=200)
    description=models.TextField()
    slug=models.SlugField()

    def get_absolute_url(self):
        return reverse("core:category",kwargs={
            'slug':self.slug
        })

    def __str__(self):
        return self.title
########################################   
class Brand(models.Model):
    brand_name=models.CharField(max_length=200)
    slug=models.SlugField()

    def get_absolute_url(self):
        return reverse("core:brand",kwargs={
            'slug':self.slug
        })

    def __str__(self):
        return self.brand_name
##############################################
LABEL_CHOICE=(
    ('P',"primary"),
    ('s',"secondry"),
    ('d',"danger"),
)
class Item(models.Model):
    title=models.CharField(max_length=200)
    category=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,blank=True)
    label=models.CharField(choices=LABEL_CHOICE,max_length=1)
    slug=models.SlugField()
    description=models.TextField()
    image=models.ImageField()
    price=models.IntegerField()
    discount_price=models.FloatField(null=True,blank=True)
   

    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse("core:item",kwargs={
            'slug':self.slug
        })   
#########################

class Variation(models.Model):
    item=models.ForeignKey(Item,on_delete=models.CASCADE)
    name=models.CharField(max_length=200)
    
    def __str__(self):
        return self.name

#############################

class ItemVariation(models.Model):
    variation=models.ForeignKey(Variation,on_delete=models.CASCADE)
    value=models.CharField(max_length=200)#L,M,S,XL,RED,
    attachment=models.ImageField(blank=True)
    class Meta:
        unique_together=(
            ('variation','value')
        )

    def __str__(self):
        return self.value

##################

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    ordered=models.BooleanField(default=False)
    item=models.ForeignKey(Item,on_delete=models.CASCADE)
    qty=models.IntegerField(default=1)
    item_variations=models.ManyToManyField(ItemVariation)

    
############

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    ref_code=models.CharField(max_length=200)
    items=models.ManyToManyField(OrderItem)
    start_date=models.DateTimeField(auto_now_add=True)
    address=models.ForeignKey("Address",related_name="shipping_address",on_delete=models.SET_NULL,blank=True,null=True)
    payment=models.ForeignKey("Payment",on_delete=models.SET_NULL,blank=True,null=True)
    coupon=models.ForeignKey("Coupon",on_delete=models.SET_NULL,blank=True,null=True)
    ordered=models.BooleanField(default=False)
    being_delivered=models.BooleanField(default=False)
    recieved=models.BooleanField(default=False)
    refund_required=models.BooleanField(default=False)
    refund_granted=models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
##################
CITY_CHOICE=(
    ("PR","purnea"),
    ("PAT","Patna"),
   
)
STATE_CHOICE=(
    ("br","Bihar"),
    ("dl","Delhi"),
    ("dl","Delhi"),
)
ADDRESS_CHOICE=(
    ("H","HOME"),
    ("O","OFFICE"),
)
class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    name=models.CharField(max_length=200)
    contact=models.IntegerField()
    pincode=models.IntegerField()
    locality=models.CharField(max_length=200)
    street_address=models.TextField()
    city=models.CharField(choices=CITY_CHOICE,max_length=20)
    city=models.CharField(choices=STATE_CHOICE,max_length=20)
    landmarks=models.CharField(max_length=200,blank=True,null=True)
    alternative_no=models.IntegerField(blank=True,null=True)
    address_type=models.CharField(choices=ADDRESS_CHOICE,blank=True,null=True,max_length=1)
    default=models.BooleanField(default=False)

    class Meta:
        verbose_name_plural="Addresses"


#########################

class Payment(models.Model):
    text_id=models.CharField(max_length=200)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    amount=models.IntegerField()
    timestamp=models.DateTimeField(auto_now_add=True)

###########################
class Coupon(models.Model):
    code=models.CharField(max_length=200)
    amount=models.FloatField()
    def __str__(self):
        return self.code
################

class Refund(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    reason=models.TextField()
    accepted=models.BooleanField(default=False)
    email=models.EmailField()

    def __str__(self):
        return f"{self.pk}"
