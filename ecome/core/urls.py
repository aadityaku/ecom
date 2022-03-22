
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
    path("delete-from-cart/<slug>/",RemoveItem,name="delete-from-cart"),
]
