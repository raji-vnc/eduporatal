from locale import currency
from django.contrib import messages
from venv import create
from django.shortcuts import redirect, render
from django.shortcuts import render, get_object_or_404
from requests import session
from .forms import CourseForm
from .models import Course, Enrollment,Payment
import stripe
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.views.decorators.http import require_POST
import logging
from django.conf import settings
stripe.api_key=settings.STRIPE_SECRET_KEY
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout

logger = logging.getLogger(__name__)
def home(request):
    return render(request,'index.html')

def course_page(request):
    course=Course.objects.all()
    return render(request,'customer_course.html',{
        'course':course
    })

def course_single_page(request,id):
    course=get_object_or_404(Course,id=id)
    return render(request,'customer_course_detail.html',{
        'course':course
    })

@login_required
def enroll_course(request,id):
    course=Course.objects.get(id=id)

    if course.course_type=='free':
        Enrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={'paid':True}
        )
        return redirect('course_detail',id)
    return redirect('payment_page',id)
   
@login_required
def course_materials(request,id):
    course=get_object_or_404(Course,id=id)
    user=request.user
    try:
        enrollment = Enrollment.objects.get(user=user, course=course)
        if not enrollment.paid:
            # Not paid yet — redirect to payment page
            return redirect('course_payment', id=course.id)
    except Enrollment.DoesNotExist:
        # Not enrolled — redirect to enroll page
        return redirect('enroll_course', id=course.id)

    # User has access, render course materials
    return render(request, 'course_materials.html', {'course': course})
@login_required
def course_payment(request,id):
    course = get_object_or_404(Course, id=id)
    user = request.user

    if request.method == 'POST':
        # Process payment here (integrate payment gateway)
        # On success:
        enrollment, created = Enrollment.objects.get_or_create(user=user, course=course)
        enrollment.paid = True
        enrollment.save()
        return redirect('course_materials', id=course.id)

    return render(request,'course_payment.html', {'course': course})

@login_required
def create_checkout_session(request, id):
    course = get_object_or_404(Course, id=id)
    amount_in_paise = int(course.price * 100) 
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        mode='payment',
        line_items=[{
            'price_data':{
                'currency':'inr',
                'product_data':{
                    'name':course.title,
                },
                'unit_amount':amount_in_paise,
            },
            'quantity':1
        }],
        success_url="http://127.0.0.1:8000/payment-success/?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="http://127.0.0.1:8000/payment-cancel/",
    )

    return redirect(session.url)

@login_required
def payment_page(request, id):
    course = get_object_or_404(Course, id=id)
    return render(request, 'payment_page.html', {'course': course})
@login_required
def payment_success(request):
  
    session_id = request.GET.get("session_id")

    if not session_id:
        return redirect("home")   # or any safe page

    session = stripe.checkout.Session.retrieve(session_id)

    # Get course id from metadata (best method)
    course_id = session.metadata.get("course_id")

    if not course_id:
        return redirect("course_detail", id=course_id)
    session = stripe.checkout.Session.retrieve(session_id)
    payment_intent = session.payment_intent
    amount_total = session.amount_total / 100  # Convert to main currency unit

    # Save payment details to database
    Payment.objects.create(
        user=request.user,
        payment_intent=payment_intent,
        amount=amount_total,
        status="completed"
    )

    return redirect("course_detail",session.metadata.get(course_id))

def payment_cancel(request):
    return render(request, 'payment_cancel.html')
def get_payment_status(request, id):
    enrollment = get_object_or_404(Enrollment, user=request.user, course_id=id)
    return JsonResponse({'paid': enrollment.paid})

@login_required
def course_detail(request, id):
    course = get_object_or_404(Course, id=id)
    enrollment = Enrollment.objects.filter(
        user=request.user,
        course=course
    ).first()

    print("DEBUG course_detail")
    print("Enrollment exists:", enrollment)
    if enrollment:
        print("Paid value:", enrollment.paid)

    if course.course_type == 'paid':
        if not enrollment:
            print("Redirecting to payment (no enrollment)")
            return redirect('payment_page', id=id)

        if not enrollment.paid:
            print("Redirecting to payment (not paid)")
            return redirect('payment_page', id=id)

    print("Showing course content")
    contents = course.contents.all()

    return render(request, 'course_detail.html', {
        'course': course,
        'contents': contents,
        'enrollment': enrollment
    })


def register(request):
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Account created successfully')
            username=form.cleaned_data.get('username')
            password=form.cleaned_data.get('password1')
            user=authenticate(username=username,password=password)
            login(request,user)
            return redirect('home')
    else:
        form=UserCreationForm()
    return render(request,'signup.html',{
        'form':form
    })
def login_view(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'Invalid username or password')
    return render(request,'login.html')
def logout_view(request):
    logout(request)
    return redirect('home')