from locale import currency
from venv import create
from django.shortcuts import redirect, render
from django.shortcuts import render, get_object_or_404
from requests import session
from .forms import CourseForm
from .models import Course, Enrollment
import stripe
from django.http import HttpResponseForbidden 
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

@login_required
def payment_success(request,id):
    course = get_object_or_404(Course, id=id)

    print("DEBUG payment_success")

    Enrollment.objects.update_or_create(
        user=request.user,
        course=course,
        defaults={'paid': True}
    )

    return redirect('course_detail', id=id)


def payment_cancel(request,id):
    return render(request,'payment_cancel.html')
@login_required
def payment_page(request,id):
    course=get_object_or_404(Course,id=id)
    session=stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data':{
                'currency':'inr',
                'product_data':{
                    'name':course.title,
                },
                'unit_amount':int(course.price*100),
            },
           'quantity':1 ,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(f'/course/{course.id}/payment-cancel'),
        cancel_url=request.build_absolute_uri(f'/course/{course.id}/payment-cancel/'),
    )
    return render(request,'payment_page.html',{
        'course':course,
        'session_id':session.id,
        'stripe_public_key':settings.STRIPE_PUBLIC_KEY
    })

@login_required
@require_POST
def create_checkout_session(request,id):
    course=get_object_or_404(Course,id=id)
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'inr',
                'product_data': {
                    'name': course.title,
                },
                'unit_amount': int(course.price * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(
            f'/course/{course.id}/payment-success/'
        ),
        cancel_url=request.build_absolute_uri(
            f'/course/{course.id}/payment/'
        ),
    )

    return JsonResponse({
        'id': session.id
    })

