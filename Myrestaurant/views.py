from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Menu, Vendor, Client, Order
from django.contrib.auth import authenticate, login, logout

# Home page
def index(request):
    return render(request, 'index.html')

# Client view for browsing menus and placing orders
def browse_menus(request):
    menus = Menu.objects.all()
    vendors = Vendor.objects.all()
    vendor_id = request.GET.get('vendor')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if vendor_id:
        menus = menus.filter(vendor_id=vendor_id)
    if min_price:
        menus = menus.filter(price__gte=min_price)
    if max_price:
        menus = menus.filter(price__lte=max_price)

    context = {
        'menus': menus,
        'vendors': vendors,
        'selected_vendor': vendor_id,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'browse_menus.html', context)


@login_required
def place_order(request, menu_id):
    menu = get_object_or_404(Menu, pk=menu_id)
    try:
        client = Client.objects.get(user=request.user)
    except ObjectDoesNotExist:
        messages.error(request, "You need to login as a client to place orders.")
        return redirect('login')

    order_success = False  # Track if order was just placed

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        contact = request.POST.get("contact")
        location = request.POST.get("location")
        if not contact or not location:
            messages.error(request, "Contact and Location information is required.")
        else:
            Order.objects.create(client=client, menu=menu, quantity=quantity, contact=contact, location=location)
            order_success = True

    context = {
        'menu': menu,
        'order_success': order_success,
    }
    return render(request, 'place_order.html', context)


# Vendor view for managing menus
def vendor_dashboard(request):
    # Ensure the logged-in user is a vendor
    vendor = get_object_or_404(Vendor, user=request.user)

    # Retrieve menus and orders associated with the vendor
    menus = Menu.objects.filter(vendor=vendor)
    orders = Order.objects.filter(menu__vendor=vendor)

    return render(request, 'vendor_dashboard.html', {'menus': menus, 'orders': orders, 'vendor': vendor})


def manage_menu(request, menu_id=None):
    vendor = get_object_or_404(Vendor, user=request.user)
    menu = Menu.objects.get(pk=menu_id) if menu_id else None

    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        image = request.FILES.get("image")
        description = request.POST.get("description")

        if menu:
            # Update existing menu
            menu.name = name
            menu.price = price
            if image:
                menu.image = image
            menu.save()
        else:
            # Create a new menu
            Menu.objects.create(name=name, price=price, image=image, description=description, vendor=vendor)

        return redirect('vendor_dashboard')

    return render(request, 'manage_menu.html', {'menu': menu})


def registration(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST['email']
        password = request.POST.get('password')
        password1 = request.POST.get('password1')
        role = request.POST.get('role')
        contact = request.POST.get('contact')
        restaurant_name = request.POST.get('restaurant_name', '')

        if password == password1:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Already Used')
                return redirect('registration')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Already Used')
                return redirect('registration')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                if role == 'client':
                    Client.objects.create(user=user, contact=contact)
                elif role == 'vendor':
                    Vendor.objects.create(user=user, restaurant_name=restaurant_name, contact=contact)
                return redirect('login')
        else:
            messages.info(request, 'Passwords do not match')
            return redirect('registration')
    return render(request, 'registration.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST.get('role')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if role == 'client':
                if not hasattr(user, 'client'):
                    messages.error(request, 'You are not registered as a client.')
                    return render(request, 'login.html')
                login(request, user)
                return redirect('browse_menus')
            elif role == 'vendor':
                if not hasattr(user, 'vendor'):
                    messages.error(request, 'You are not registered as a vendor.')
                    return render(request, 'login.html')
                login(request, user)
                return redirect('vendor_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    return redirect('browse_menus')


def delete_menu(request, menu_id):
    menu = get_object_or_404(Menu, pk=menu_id)
    if request.method == "POST" and menu.vendor.user == request.user:
        menu.delete()
        return redirect('vendor_dashboard')

def edit_menu(request, menu_id):
    menu = get_object_or_404(Menu, pk=menu_id, vendor__user=request.user)
    if request.method == "POST" and menu.vendor.user == request.user:
        menu.name = request.POST.get("name", menu.name)
        menu.price = request.POST.get("price", menu.price)  
        menu.description = request.POST.get("description", menu.description)
        menu.image = request.FILES.get("image") 
        menu.save() 
        return redirect('vendor_dashboard')
    return render(request, 'manage_menu.html', {'menu': menu})


def menu_details(request, menu_id):
    menu = get_object_or_404(Menu, id=menu_id)
    return render(request, 'menu_details.html', {'menu': menu})


# cart functions


@login_required
def add_to_cart(request, menu_id):
    cart = request.session.get('cart', {})
    quantity = int(request.POST.get('quantity', 1))
    cart[str(menu_id)] = cart.get(str(menu_id), 0) + quantity
    request.session['cart'] = cart
    return redirect('browse_menus')

@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    menus = Menu.objects.filter(id__in=cart.keys()).select_related('vendor')
    # Group items by vendor
    restaurant_groups = {}
    for menu in menus:
        vendor_id = menu.vendor.id
        vendor_name = menu.vendor.restaurant_name
        if vendor_id not in restaurant_groups:
            restaurant_groups[vendor_id] = {
                'vendor_name': vendor_name,
                'items': []
            }
        restaurant_groups[vendor_id]['items'].append({
            'menu': menu,
            'quantity': cart[str(menu.id)]
        })
    return render(request, 'cart.html', {'restaurant_groups': restaurant_groups})

@login_required
def place_cart_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('browse_menus')
    vendor_id = request.POST.get('vendor_id')
    client = Client.objects.get(user=request.user)
    contact = request.POST.get('contact')
    location= request.POST.get('location')
    menus = Menu.objects.filter(id__in=cart.keys(), vendor_id=vendor_id)
    for menu in menus:
        quantity = cart[str(menu.id)]
        Order.objects.create(client=client, menu=menu, quantity=quantity, contact=contact, location=location)
        # Remove ordered item from cart
        del cart[str(menu.id)]
    request.session['cart'] = cart  # Update cart in session
    messages.success(request, "Order placed for selected restaurant!")
    return redirect('browse_menus')

@login_required
@require_POST
def mark_order_delivered(request, order_id):
    order = get_object_or_404(Order, id=order_id, menu__vendor__user=request.user)
    order.status = "delivered"
    order.save()
    messages.success(request, "Order marked as delivered.")
    return redirect('vendor_dashboard')