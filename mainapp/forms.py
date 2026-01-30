from django import forms
from .models import Course

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'image', 'description', 'course_type', 'is_active']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'course_type': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(),
        }
