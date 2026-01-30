from email.policy import default
from turtle import update
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
User = get_user_model()
class Course(models.Model):
    
    COURSE_TYPE_CHOICES = (
        ('free', 'Free'),
        ('premium', 'Premium'),
    )
    image=models.ImageField(upload_to='courses/',null=True,blank=True)
    description = models.TextField(blank=True)
    title = models.CharField(max_length=200)
    course_type = models.CharField(
        max_length=10,
        choices=COURSE_TYPE_CHOICES,
        default='free'
    )
    price=models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class Message(models.Model):

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"
    
class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=False)
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    paid=models.BooleanField(default=False)
    enrolled_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user','course')
    def __str__(self):
        return f"{self.user}{self.course}({'Paid' if self.paid else 'Not Paid'})"

class Course_Material(models.Model):
    course=models.ForeignKey(Course,related_name='materials',on_delete=models.CASCADE)
    material_type=models.CharField(max_length=20,choices=[('pdf','PDF'),('video','VIDEO'),('note','NOTE')])
    title=models.CharField(max_length=200)
    file=models.FileField(upload_to='course_materials/',blank=True,null=True)
    url=models.URLField(blank=True,null=True)
    description=models.TextField(blank=True,null=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Course_Content(models.Model):
    CONTENT_TYPE_CHOICE=(
        ('video','Video'),
        ('pdf','PDF/Notes'),
    )
    course=models.ForeignKey(
        Course,on_delete=models.CASCADE,related_name='contents'
    )
    title=models.CharField(max_length=200)
    content_type=models.CharField(max_length=10,choices=CONTENT_TYPE_CHOICE)
    video_file=models.FileField(upload_to='course_videos/',null=True,blank=True)
    pdf_file=models.FileField(upload_to='course_notes/',null=True,blank=True)
    order=models.PositiveBigIntegerField(default=1)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['order']
    def __str__(self):
        return f"{self.course.title} - {self.title}"