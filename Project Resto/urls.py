from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.browse_menus, name='home'), 
    path('browse_menus/', views.browse_menus, name='browse_menus'),
    path('registration/', views.registration, name='registration'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('menu/<int:menu_id>/', views.menu_details, name='menu_details'),
    path('place_order/<int:menu_id>/', views.place_order, name='place_order'),
    path('vendor/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/manage/<int:menu_id>/', views.manage_menu, name='manage_menu'),
    path('vendor/manage/', views.manage_menu, name='manage_menu_create'),  # Add menu creation
    path('vendor/delete/<int:menu_id>/', views.delete_menu, name='delete_menu'),
    path('vendor/edit/<int:menu_id>/', views.edit_menu, name='edit_menu'),
    path('add_to_cart/<int:menu_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/place_order/', views.place_cart_order, name='place_cart_order'),
    path('vendor/order/delivered/<int:order_id>/', views.mark_order_delivered, name='mark_order_delivered'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
