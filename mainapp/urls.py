from django.urls import path
from . import views as app_views
from .views import home,course_page,course_single_page,enroll_course,course_detail,course_materials,course_payment,create_checkout_session,payment_page,payment_success,payment_cancel,get_payment_status
from django.contrib.auth import views as auth_views
urlpatterns = [
path('',home,name='home'),
path('course_page/',course_page,name='course_page'),
path('course_single_page/<int:id>/',course_single_page,name='course_single_page'),
path('enroll_course/<int:id>/',enroll_course,name="enroll_course"),
path('course_detail/<int:id>/',course_detail,name="course_detail"),
path('course_materials/<int:id>/',course_materials,name="course_materials"),
path('course_payment/<int:id>/',course_payment,name='course_payment'),
path('create-checkout-session/<int:id>/',create_checkout_session,name='create_checkout_session'),
path('payment-success/',payment_success,name='payment_success'),
path('payment-cancel/',payment_cancel,name='payment_cancel'),
path('get-payment-status/<int:id>/',get_payment_status,name='get_payment_status'),
path('payment_page/<int:id>/',payment_page,name='payment_page'),
path('register/', app_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]
