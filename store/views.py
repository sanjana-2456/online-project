from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Order, OrderItem
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .cart import Cart
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .forms import CheckoutForm
from rapidfuzz import fuzz 
from django.urls import reverse
from django.http import JsonResponse


@login_required(login_url='/accounts/login/') 
def profile(request):
    return render(request, 'profile.html', {'user': request.user})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.add(product=product)
    return redirect('cart_detail')


@login_required
def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart.html', {'cart': cart})


@login_required
def cart_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.remove(product)
    return redirect('cart_detail')


@login_required
def cart_update(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart = Cart(request)
        action = request.POST.get("action")

        if action == "increase":
            cart.add(product=product, quantity=1, override_quantity=False)
        elif action == "decrease":
            if cart.cart.get(str(product_id), {}).get('quantity', 0) > 1:
                cart.add(product=product, quantity=-1, override_quantity=False)
            else:
                cart.remove(product)
        return redirect('cart_detail')
    return redirect('cart_detail')


@login_required
def checkout(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            cart.clear()
            return redirect('order_detail', order_id=order.id)
    else:
        form = CheckoutForm()
    return render(request, 'checkout.html', {'cart': cart, 'form': form})


@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    total_price = sum(item.price * item.quantity for item in order.items.all())
    return render(request, 'order_detail.html', {'order': order, 'total_price': total_price})


def home(request):
    query = request.GET.get('q')
    category_slug = request.GET.get('category')

    products = Product.objects.all()
    cart = Cart(request)
    cart_product_ids = [int(pid) for pid in cart.cart.keys()]

    if query:
        results = []
        for product in products:
            similarity = fuzz.partial_ratio(query.lower(), product.name.lower())
            if similarity > 70:
                results.append((product, similarity))
        results.sort(key=lambda x: x[1], reverse=True)
        products = [r[0] for r in results]

    if category_slug:
        products = products.filter(category__slug=category_slug)

    categories = Category.objects.all()
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    carousel_images = [
        '/static/images/banner 1.jpg',
        '/static/images/banner 2.jpg',
        '/static/images/banner 3.jpg',
        '/static/images/banner 4.jpg',
    ]

    return render(request, 'home.html', {
        'products': page_obj,
        'categories': categories,
        'cart_product_ids': cart_product_ids,
        'carousel_images': carousel_images,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})


def about(request):
    return render(request, 'about.html', {
        'title': 'About Us',
        'content': 'This is a simple chat application built with Django.'
    })


def product_suggestions(request):
    query = request.GET.get("q", "")
    if query:
        products = Product.objects.all()
        results = []
        for product in products:
            similarity = fuzz.partial_ratio(query.lower(), product.name.lower())
            if similarity > 70:
                results.append((product, similarity))
        results.sort(key=lambda x: x[1], reverse=True)
        products = [r[0] for r in results]
        suggestions = [
            {"name": product.name, "url": reverse("product_detail", args=[product.id]), "image": product.image.url if product.image else ""}
            for product in products
        ]
    else:
        suggestions = []
    return JsonResponse(suggestions, safe=False)


# ✅ BUY NOW VIEW
@login_required
def buy_now(request, product_id):
     product = get_object_or_404(Product, id=product_id)
     cart = Cart(request)
     cart.clear()
     cart.add(product=product, quantity=1, override_quantity=True)
     return redirect('checkout')
