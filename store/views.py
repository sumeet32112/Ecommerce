from django.db.models.fields import DateTimeField
from django.http.response import JsonResponse
from django.shortcuts import render,redirect
from .models import *
from django.http import HttpResponse,HttpResponseRedirect, request
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
import json
import datetime
from django.contrib import messages
from .forms import NewUserForm
from django.contrib.auth.models import User

def user_login(request):
    data={}
    if request.method=="POST":
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request,username=username,password=password)
        if user:
            login(request,user)
            request.session['username']=username
            return HttpResponseRedirect('store')
        else:
           data['error']="username or password is incorrect"
           res=render(request,'store/login.html',data)
           return res
    else:
        return render(request,'store/login.html',data)


def userlogout(request):
    logout(request)
    return HttpResponseRedirect('/')  

@login_required(login_url="login")
def store(request):
    customer=request.user.customer
    order,created=Order.objects.get_or_create(customer=customer,complete=False)
    items=order.orderitem_set.all()
    cartItems=order.get_cart_items
    products=Product.objects.all()
    context={"products":products,"cartItems":cartItems}
    return render(request,'store/store.html',context)

@login_required(login_url="login")
def cart(request):
        customer=request.user.customer
        order,created=Order.objects.get_or_create(customer=customer,complete=False)
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
        context={'items':items,'order':order,"cartItems":cartItems}
        return render(request,'store/cart.html',context)

@login_required(login_url="login")
def checkout(request):
    customer=request.user.customer
    order,created=Order.objects.get_or_create(customer=customer,complete=False)
    items=order.orderitem_set.all()
    cartItems=order.get_cart_items
    context={'items':items,'order':order,"cartItems":cartItems}
    return render(request,'store/checkout.html',context)

@login_required(login_url="login")
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
	
    if action == 'add':
    	orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
    	orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
    	orderItem.delete()

    return JsonResponse('Item was added...', safe=False)

@login_required(login_url="login")
def processOrder(request):
    transaction_id=datetime.datetime.now().timestamp()
    data=json.loads(request.body)

    customer=request.user.customer
    order,created=Order.objects.get_or_created(customer=customer,complete=False)

    total=data['form']['total']
    order.transaction_id=transaction_id

    if total==order.get_cart_total:
        order.complete=True
    order.save()

    ShippingAddress.objects.create(
        customer=customer,
        order=order,
        address=data['shipping']['address'],
        city=data['shipping']['city'],
        state=data['shipping']['state'],
        zipcode=data['shipping']['zipcode'],
    )    
    return JsonResponse('payment submitted....',safe=False)    

def signup(request):
    if request.method=="POST":
        form=NewUserForm(request.POST)
        if form.is_valid():
            user=form.save() 
            customer,created=Customer.objects.get_or_create(user=user)
            customer.email=request.POST['email']
            customer.name=request.POST['username']
            customer.save()
            login(request,user)
            messages.success(request,"registration is successful..")
            return redirect('/')
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render (request,"store/register.html",{"register_form":form})    