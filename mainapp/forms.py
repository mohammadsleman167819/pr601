from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email","role")

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email","role")

from django import forms
from datetime import date


class EmployeeInfoForm(forms.Form):
    firstname = forms.CharField(label="First Name", max_length=100, help_text='Employee First Name')
    lastname = forms.CharField(label="Last Name", max_length=100, help_text='Employee Last Name')
    dateOfBirth = forms.DateField(label="Date Of Birth", help_text='Employee Date of Birth')
    gender = forms.ChoiceField(choices=[('MALE', 'MALE'), ('FEMALE', 'FEMALE')], label="Gender")
    city = forms.CharField(label="City", max_length=50, help_text='Employee City')
    phone = forms.CharField(label="Phone", max_length=20,min_length=10, help_text='Employee Phone')
    education = forms.CharField(widget=forms.Textarea,label="Education", max_length=1000, required=False)  
    experience = forms.CharField(widget=forms.Textarea,label="Experience", max_length=1000, required=False)  
    awards = forms.CharField(widget=forms.Textarea,label="Awards", max_length=1000, required=False)  
    hobbies = forms.CharField(widget=forms.Textarea,label="Hobbies", max_length=1000, required=False)  
    skills = forms.CharField(widget=forms.Textarea,label="Skills", max_length=1000)
    references = forms.CharField(widget=forms.Textarea,label="References", max_length=1000, required=False)  
    other = forms.CharField(widget=forms.Textarea,label="Other", max_length=1000, required=False)  
    def clean_phone(self):
        data = self.cleaned_data['phone']

        for char in data:
           if not char.isdigit() and char not in '-+':
                raise ValidationError('Phone number can only contain digits, hyphens, and plus signs.')

        return data

    def clean_date_of_birth(self):       
        data = self.cleaned_data['date_of_birth']
        today = date.today()
        if data > today:
            raise ValidationError('Date of birth cannot be in the future.')
        minimum_age = 16 
        maximum_age = 120  
        
        age = today.year - data.year - ((today.month, today.day) < (data.month,data.day))
        if age < minimum_age:
            raise ValidationError(f'You must be at least {minimum_age} years old to register.')
        if age > maximum_age:
            raise ValidationError(f'{age} years old is not a valid value.')

        return data


class CompanyInfoForm(forms.Form):
    name  = forms.CharField(label="Comapany Name",max_length=100) 
    city = forms.CharField(label="City", max_length=50)
    phone = forms.CharField(label="Phone", max_length=20,min_length=10)
    

    def clean_phone(self):
        data = self.cleaned_data['phone']

        for char in data:
           if not char.isdigit() and char not in '-+':
                raise ValidationError('Phone number can only contain digits, hyphens, and plus signs.')

        return data

    
class Job_PostCreateForm(forms.Form):
    
    job_title = forms.CharField(label="Job Title",max_length=50) 
    jobDescription = forms.CharField(widget=forms.Textarea,label="Job Description", max_length=1000)
    workhours = forms.CharField(widget=forms.Textarea,label="Work Hours", max_length=1000)
    contact = forms.CharField(label="Contact",max_length=50)
    city = forms.CharField(label="City", max_length=50)
    salary = forms.CharField(label="Salary", max_length=50)
    

class CourseCreateForm(forms.Form):
    
    courseTitle = forms.CharField(label="Course Title",max_length=50)
    description  = forms.CharField(widget=forms.Textarea,label="Course Description", max_length=1000)
    link = forms.CharField(label="Course Link", max_length=100)
import csv    
import os
from .models import Job_Post

class TrainModelForm(forms.Form):
    #data_file = forms.FileField(label="job posts cvs file",help_text="make sure your cvs file has all job_posts fields(job_titl,jobDescription,workhours,contact,city,salary)",required=False)
    #company_id = forms.IntegerField(label="company id",help_text="the company_id this data related to",required=False)
    number_of_clusters = forms.IntegerField(label="number_of_clusters",required=True)
    word2vec_vector_size = forms.IntegerField(label="word2vec vector size",help_text="2500 recomended",required=True)
    word2vec_window_size = forms.IntegerField(label="word2vec window size",help_text="12 recomended",required=True)
    word2vec_word_min_count = forms.IntegerField(label="word2vec word_min_count",help_text="proptional to number of rows divided by number of clusters,-1 for auto compute",required=True)
    start_date = forms.DateField()

    def __init__(self, *args, **kwargs):
        super(TrainModelForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].initial = self.get_min_added_date()

    def get_min_added_date(self):
        min_date = Job_Post.objects.filter(added_date__isnull=False).order_by('added_date').first()
        if min_date:
            return min_date.added_date
        else:
            # Handle case where no Job_Posts exist (optional)
            return date.today()  # Or set another default value
      
    '''def clean_data_file(self):
        data_file = self.cleaned_data['data_file']
        print(data_file)
        if data_file:            
            extension = os.path.splitext(data_file.name)[1].lower()
            if extension not in ('.csv',):
                raise ValidationError('Only CSV files are allowed.')
            required_columns = ['job_title','jobDescription','workhours','contact','city','salary']
            try:
                reader = csv.reader(data_file)
                headers = next(reader)  # Read the first row as headers
                if not all(col in headers for col in required_columns):
                    raise ValidationError(f"Missing required columns: {', '.join(set(required_columns) - set(headers))}")
            except csv.Error as e:
                raise ValidationError(f"Invalid CSV file: {e}")
        else:
            rows = Job_Post.objects.count()
            if rows == 0:
                raise ValidationError('no data to train , and no file added')

        return data_file'''