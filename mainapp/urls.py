from django.urls import path
from .views import home,course_page,course_single_page,enroll_course,course_detail,course_materials,course_payment,payment_page,payment_success,payment_cancel,create_checkout_session

urlpatterns = [
path('',home,name='home'),
path('course_page/',course_page,name='course_page'),
path('course_single_page/<int:id>/',course_single_page,name='course_single_page'),
path('enroll_course/<int:id>/',enroll_course,name="enroll_course"),
path('course_detail/<int:id>/',course_detail,name="course_detail"),
path('course_materials/<int:id>/',course_materials,name="course_materials"),
path('course_payment/<int:id>/',course_payment,name='course_payment'),
path('payment_page/<int:id>/',payment_page,name='payment_page'),
path('course/<int:id>/payment-success/', payment_success, name='payment_success'),
path('payment_cancel/<int:id>/',payment_cancel,name='payment_cancel'),
path('create_checkout_session/<int:id>/',create_checkout_session,name='create_checkout_session'),

]
