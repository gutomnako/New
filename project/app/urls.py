from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerPage, name='register'),
    #path('home/', views.index, name='home'),

    path('rate_resort/<int:resort_id>/', views.rate_resort, name='rate_resort'),

    path('home/', views.home, name='home'),
    path('', views.index_view, name='index-view'),
    path('resort/<str:pk>/', views.resort, name='resort'),
    path('profile/<str:pk>/', views.userProfile, name='user-profile'),

    path('create-resort/', views.createResort, name='create-resort'),
    path('update-resort/<str:pk>/', views.updateResort, name='update-resort'),
    path('filter-beaches/', views.filter_beaches, name='filter_beaches'),
    path('delete-resort/<str:pk>/', views.deleteResort, name='delete-resort'),
    path('delete-message/<str:pk>/', views.deleteMessage, name='delete-message'),
    path('contact-number/', views.contact_number, name='contact-number'),

    path('update-user/', views.updateUser, name='update-user'),

    path('admin-Dashboard/', views.adminDashboard, name='admin-dashboard'),
    path('adminbeachandresort/', views.adminresorts, name='admin-beach'),
    path('adminviews/', views.adminmonitors, name='admin-monitor')
    
]