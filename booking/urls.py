from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.room_list_view, name='room_list'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),    
    path('book/<int:room_id>/', views.book_room_view, name='book_room'),
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('cancel/<int:booking_id>/', views.cancel_booking_view, name='cancel_booking'),
    path('admin-view/', views.admin_room_bookings_view, name='admin_room_view'),
    path('rooms/add/', views.add_room_view, name='add_room'),
    path('rooms/<int:room_id>/edit/', views.edit_room_view, name='edit_room'),
]