from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerPage, name='register'),

    # path('recommended/', views.recommended_resorts, name='recommended_resorts'),

    #path('resorts/', views.resort_list, name='resort_list'),
    path('rate_resort/<int:resort_id>/', views.rate_resort, name='rate_resort'),
    path('toggle_favorite/', views.toggle_favorite, name='toggle_favorite'),

    path('home/', views.home, name='home'),
    path('', views.index_view, name='index-view'),
    path('resort/<int:pk>/', views.resort, name='resort'),  # Make sure 'resort' matches the redirect name
    path('resort/<int:pk>/update/', views.update_resort, name="update_resort"),
    path('profile/<int:pk>/', views.userProfile, name='user-profile'),

    path('create-resort/', views.createResort, name='create-resort'),
    path('update-resort/<str:pk>/', views.updateResort, name='update-resort'),
    path('filter-beaches/', views.filter_beaches, name='filter_beaches'),
    path('delete-resort/<str:pk>/', views.deleteResort, name='delete-resort'),
    path('delete-message/<str:pk>/', views.deleteMessage, name='delete-message'),
    path('contact-number/', views.contact_number, name='contact-number'),

    path('update-user/', views.updateUser, name='update-user'),

    path('admin-Dashboard/', views.adminDashboard, name='admin-dashboard'),
    path('adminbeachandresort/', views.adminresorts, name='admin-beach'),
    path('adminviews/', views.adminmonitors, name='admin-monitor'),
    
    path('map/', views.map_view, name='map'),

    path("resort/update/<int:resort_id>/", views.update_resort, name="update_resort"),
    path("update_resort_inline/<int:pk>/", views.update_resort_inline, name="update_resort_inline"),
    path("update_resort_image/<int:pk>/", views.update_resort_image, name="update_resort_image"),
]
