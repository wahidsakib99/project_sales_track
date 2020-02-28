from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('register/',views.register_page,name="register_page"),# returns register page
    path('register/verify_register/',views.verify_register,name="verify_register"),
    path('',views.return_login_page,name = "return_login_page"), # Returns login page
    path('verify_login/',views.verify_login,name="verify_login"), #Verify login request
    path('dashboard/',views.dashboard, name="Dashboard"), # dashboard URL
    path('statistics/',views.statistics,name = "statistics"), # Statistics page
    path('sellerdata/',views.seller_data,name="seller_data"),
    path('logout/',views.logout,name="logout"),

    # URLS for ajax
    path('ajax/return_bar_data',views.ajax_return_bar_data, name ="return_bar_data"),
    path('ajax/return_pie_data',views.ajax_return_pie_data,name="return_pie_data"),
    path('ajax/return_data_for_statistics',views.ajax_return_data_for_statistics,name="return_data_for_statistics"),
    path('ajax/return_live_data',views.ajax_return_live_data,name = "return_live_data")
]