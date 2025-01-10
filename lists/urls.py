from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('explore/', views.explore, name='explore'),
    path('create/', views.create_list, name='create_list'),
    path('create/generate/', views.generate_list_content, name='generate_list_content'),
    path('list/<int:pk>/', views.list_detail, name='list_detail'),
    path('list/<int:pk>/fork/', views.fork_list, name='fork_list'),
    path('list/<int:pk>/edit/', views.edit_list, name='edit_list'),
    path('list/<int:pk>/delete/', views.delete_list, name='delete_list'),
    path('list/<int:pk>/like/', views.toggle_like, name='toggle_like'),
    path('list/<int:pk>/toggle-visibility/', views.toggle_visibility, name='toggle_visibility'),
    path('my-public-lists/', views.my_public_lists, name='my_public_lists'),
    path('user/<str:username>/lists/', views.user_lists, name='user_lists'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
] 