from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerPage, name='register'),
    path('apply-subadmin/', views.apply_subadmin, name='apply_subadmin'),

    # path('recommended/', views.recommended_resorts, name='recommended_resorts'),

    #path('resorts/', views.resort_list, name='resort_list'),
    path('rate-resort/<int:resort_id>/', views.rate_resort, name='rate_resort'),
    path('toggle_favorite/', views.toggle_favorite, name='toggle_favorite'),

    path('home/', views.home, name='home'),
    path('', views.index_view, name='index-view'),
    path('resort/<int:pk>/', views.resort, name='resort'),  
    path('resort/<int:pk>/update/', views.update_resort, name="update_resort"),
    path('profile/<int:pk>/', views.userProfile, name='user-profile'),

    path('create-resort/', views.createResort, name='create-resort'),
    path('update-resort/<str:pk>/', views.updateResort, name='update-resort'),
    path('delete-resort/<str:pk>/', views.deleteResort, name='delete-resort'),
    path('delete-message/<str:pk>/', views.deleteMessage, name='delete-message'),
    path('contact-number/', views.contact_number, name='contact-number'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),

    path('update-user/', views.updateUser, name='update-user'),

    path('admin-Dashboard/', views.adminDashboard, name='admin-dashboard'),
    path('adminbeachandresort/', views.adminresorts, name='admin-beach'),
    path('adminviews/', views.adminmonitors, name='admin-monitor'),
    path('adminviews/applications/', views.applications, name='applications'),
    path('delete-notification/<int:id>/', views.delete_notification, name='delete_notification'),
    path('mark-as-read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('unread-count/', views.unread_count, name='unread_count'),
    path('update-status/', views.update_status, name='update_status'),
    
    path('map/', views.map_view, name='map'),

    path("resort/update/<int:resort_id>/", views.update_resort, name="update_resort"),
    path("update_resort_inline/<int:pk>/", views.update_resort_inline, name="update_resort_inline"),
    path("update_resort_images/<int:pk>/", views.update_resort_images, name="update_resort_images"),

    path('resort/<int:resort_id>/upload_room_image_ajax/', views.upload_room_image_ajax, name='upload_room_image_ajax'),
    path('resort/<int:resort_id>/upload_beach_image_ajax/', views.upload_beach_image_ajax, name='upload_beach_image_ajax'),
    path('resort/<int:resort_id>/upload_activity_image_ajax/', views.upload_activity_image_ajax, name='upload_activity_image_ajax'),
]
