
from django.urls import path
from .views import *
app_name="core"
urlpatterns = [
    path("",HomeView.as_view(),name="homepage"),
    path("products/<slug>/",ItemDetailsView.as_view(),name="item"),
    path("category/<int:slug>/",CategoryView,name="category"),
    path("order-summary/",OrderSummary.as_view(),name="order-summary"),
    path("add-to-cart/<slug>/",AddToCart.as_view(),name="add-to-cart"),
    path("remove-from-cart/<slug>/",RemoveFromCart.as_view(),name="remove-from-cart"),
    path("delete-from-cart/<slug>/",MinusItemCart.as_view(),name="delete-from-cart"),
    path("add-coupon/",AddCoupon.as_view(),name="add-coupon"),
    path("remove-coupon/",RemoveCoupon.as_view(),name="remove-coupon"),
    path("checkout/",CheckoutView.as_view(),name="checkout"),
    path("checkout/paymenthandler/", paymenthandler, name="paymenthandler"),
    path("myorder/",myOrder,name="myorder"),
    path("save-address-action/",save_Address_Action,name="save_Address_Action"),
    
]
