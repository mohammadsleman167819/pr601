from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import CustomUserCreationForm,EmployeeInfoForm,CompanyInfoForm,Job_PostCreateForm,CourseCreateForm
from .models import Company, Employee, Job_Post, Course,ML_record
from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin
from .algorithms.ML import preprocess,generate_data
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from .algorithms.predicting import predict



class SignUpView(UserPassesTestMixin,CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = "registration/signup.html"
    
    def test_func(self):
        return not self.request.user.is_authenticated


def index(request):
    return render(request, 'index.html')


#====================================================
#Company VIEWS
'''
1 - first visit company form
2 - View the details of one company
3 - Edit company
''' 
#====================================================
#1- first visit company form 

def firstTimeCompanyaccess(user):
    return user.is_authenticated and user.is_company and user.is_firstvisit

@user_passes_test(firstTimeCompanyaccess)
def firstVisitCompany(request):
    if request.method == 'POST':
        form = CompanyInfoForm(request.POST)
        if form.is_valid():
            user = request.user
            user.firstvisit = 0
            user.save()
            new_company = Company.objects.create(company_id=user,**form.cleaned_data)
            new_company.save()
            return HttpResponseRedirect(reverse('index'))  
    else:
        form = CompanyInfoForm()
    return render(request, 'mainapp/create_company.html', {'form': form})

#2 - View the details of one company

class CompanyDetailView(LoginRequiredMixin,UserPassesTestMixin,generic.DetailView):
    model = Company
    context_object_name = 'Company'
    def test_func(self):
        company = self.get_object()
        return company.company_id_id == self.request.user.id


#3 - Edit company
class CompanyUpdate(LoginRequiredMixin,UserPassesTestMixin, UpdateView):
    
    model = Company
    fields = ['name','city','phone']

    def test_func(self):
        company = self.get_object()
        return company.company_id_id == self.request.user.id



#====================================================
#Employees VIEWS
'''
1 - first visit employee form
2 - list all employees
3 - View the details of one employee
4 - Edit employee
''' 
#====================================================

#1 - first visit employee form
def firstTimeEmployeeaccess(user):
    return user.is_authenticated and user.is_employee and user.is_firstvisit

@user_passes_test(firstTimeEmployeeaccess)
def firstVisitEmployee(request):
    if request.method == 'POST':
        form = EmployeeInfoForm(request.POST)
        if form.is_valid():
            user = request.user
            user.firstvisit = 0
            user.save()
            new_employee = Employee.objects.create(employee_id=user,**form.cleaned_data)
            new_employee.save()
            # Redirect to success page or dashboard after successful creation
            return HttpResponseRedirect(reverse('index'))  
    else:
        form = EmployeeInfoForm()
    return render(request, 'mainapp/create_employee.html', {'form': form})

#2 - list all employees
class EmployeeListView(LoginRequiredMixin,UserPassesTestMixin,generic.ListView):
    model = Employee
    context_object_name = 'Employee_list'
    paginate_by = 10
    def test_func(self):
        return self.request.user.is_company


#3 - View the details of one employee
class EmployeeDetailView(LoginRequiredMixin,UserPassesTestMixin,generic.DetailView):
    model = Employee
    context_object_name = 'Employee'
    
    def get_context_data(self, **kwargs):
        context = super(EmployeeDetailView, self).get_context_data(**kwargs)
        emp = self.get_object()
        context['Age'] = emp.get_age()
        return context
        
    def test_func(self):
        if self.request.user.is_employee:
            employee = self.get_object()
            return employee.employee_id_id==self.request.user.id
        else:
            return True
    
#4 - Edit employee
class EmployeeUpdate(LoginRequiredMixin,UserPassesTestMixin, UpdateView):
    
    model = Employee
    fields = ['firstname','lastname','dateOfBirth','gender',
              'city','phone','education','experience','awards',
              'hobbies','skills','references','other']

    def test_func(self):
        employee = self.get_object()
        return employee.employee_id_id == self.request.user.id
    
    def form_valid(self, form):
        response = super().form_valid(form)
        employee   = self.object
        education  = employee.education
        experience = employee.experience
        awards     = employee.awards
        skills     = employee.skills
        text = education + " " + experience + " " + awards + " " + skills
        clusterable_text = preprocess(text)
        employee.clusterable_text = clusterable_text
        employee.cluster=predict(clusterable_text)
        employee.save()
        return response
    


#====================================================
#Job_Post VIEWS
'''
1 - list all posts
2 - list all of company's posts
3 - list the posts suggested for some employee
4 - View the details of one post
5 - Create post
6 - Edit post
7 - Delete post
''' 
#====================================================


#1 - list all posts
class Job_PostListView(generic.ListView):
    model = Job_Post
    context_object_name = 'Job_Post_list'
    paginate_by = 10
    

  

#2 - list all of company's posts
class Company_Job_PostListView(LoginRequiredMixin,UserPassesTestMixin,Job_PostListView):
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(company_id_id=self.request.user.id)
    def test_func(self):
        return self.request.user.is_company
    
    def post(self, request, *args, **kwargs):
        generate_data()  # Call your function to generate data
        return redirect(self.request.path)

  
        
#3 - list the posts suggested for some employee
class Employee_Job_PostListView(LoginRequiredMixin,UserPassesTestMixin,Job_PostListView):
    def get_queryset(self):
        queryset = super().get_queryset()
        employee = get_object_or_404(Employee,pk=self.request.user.id)
        return queryset.filter(cluster=employee.cluster)
    def test_func(self):
        return self.request.user.is_employee
    



#4 - View the details of one post    
class Job_PostDetailView(generic.DetailView):
    model = Job_Post
    context_object_name = 'Job_Post'



#5 - Create post
def createpostaccess(user):
    return user.is_authenticated and user.is_company 

@user_passes_test(createpostaccess)
def Job_PostCreate(request):
    if request.method == 'POST':
        form = Job_PostCreateForm(request.POST)
        if form.is_valid():
            new_post = Job_Post.objects.create(company_id_id=request.user.id,**form.cleaned_data)
            new_post.save()
            # Redirect to success page or dashboard after successful creation
            return HttpResponseRedirect(reverse('myposts'))  
    else:
        form = Job_PostCreateForm()
    return render(request, 'mainapp/create_post.html', {'form': form})


  
#6 - Edit post
class Job_PostUpdate(LoginRequiredMixin,UserPassesTestMixin, UpdateView):
    model = Job_Post
    fields = ['job_title', 'jobDescription', 'workhours', 'contact','city','salary']
    
    def test_func(self):
        post = self.get_object()
        return post.company_id_id == self.request.user.id

    def form_valid(self, form):
        response = super().form_valid(form)
        post   = self.object
        description  = post.description
        clusterable_text = preprocess(description)
        post.clusterable_text = clusterable_text
        post.cluster=predict(clusterable_text)
        post.save()
        return response


#7 - Delete post
class Job_PostDelete(LoginRequiredMixin,UserPassesTestMixin, DeleteView):
    model = Job_Post
    success_url = reverse_lazy('myposts')
    
    def test_func(self):
        post = self.get_object()
        return post.company_id_id == self.request.user.id

#====================================================
#Courses VIEWS
'''
1 - list all courses
2 - list all of company's courses
3 - list the courses suggested for some employee
4 - View the details of one course
5 - Create course
6 - Edit course
7 - Delete course
''' 
#====================================================

#1 - list all courses
class CourseListView(generic.ListView):
    model = Course
    context_object_name = 'Course_list'
    paginate_by = 10

#2 - list all of company's courses
class Company_CourseListView(LoginRequiredMixin,UserPassesTestMixin,CourseListView):
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(company_id_id=self.request.user.id)
    def test_func(self):
        return self.request.user.is_company
    
#3 - list the courses suggested for some employee
class Employee_CourseListView(LoginRequiredMixin,UserPassesTestMixin,CourseListView):
    def get_queryset(self):
        queryset = super().get_queryset()
        employee = get_object_or_404(Employee,pk=self.request.user.id)
        return queryset.filter(cluster=employee.cluster)
    def test_func(self):
        return self.request.user.is_employee


#4 - View the details of one course
class CourseDetailView(generic.DetailView):
    model = Course
    context_object_name = 'Course'


#5 - Create course
def createcourseaccess(user):
    return user.is_authenticated and user.is_company 

@user_passes_test(createcourseaccess)
def CourseCreate(request):
    if request.method == 'POST':
        form = CourseCreateForm(request.POST)
        if form.is_valid():
            new_course = Course.objects.create(company_id_id=request.user.id,**form.cleaned_data)
            new_course.save()
            # Redirect to success page or dashboard after successful creation
            return HttpResponseRedirect(reverse('mycourses'))  
    else:
        form = CourseCreateForm()
    return render(request, 'mainapp/create_course.html', {'form': form})


  
#6 - Edit course
class CourseUpdate(LoginRequiredMixin,UserPassesTestMixin, UpdateView):
    
    model = Course
    fields = ['courseTitle', 'description', 'link',]
    
    def test_func(self):
        course = self.get_object()
        return course.company_id_id == self.request.user.id
    
    def form_valid(self, form):
        response = super().form_valid(form)
        course   = self.object
        description  = course.description
        clusterable_text = preprocess(description)
        course.clusterable_text = clusterable_text
        course.cluster=predict(clusterable_text)
        course.save()
        return response

    

#7 - Delete course
class CourseDelete(LoginRequiredMixin,UserPassesTestMixin, DeleteView):
    model = Course
    success_url = reverse_lazy('mycourses')
    permission_required = 'mainapp.delete_course'
    def test_func(self):
        course = self.get_object()
        return course.company_id_id == self.request.user.id    



#=====================================
'''
model views
'''
#=====================================
from .forms import TrainModelForm
from .algorithms.training import train_model
import threading
def train_model_view(request):
    if request.method == 'POST':
        form = TrainModelForm(request.POST)
        if form.is_valid():
            number_of_clusters = form.cleaned_data['number_of_clusters']
            word2vec_vector_size = form.cleaned_data['word2vec_vector_size']
            word2vec_window_size = form.cleaned_data['word2vec_window_size']
            word2vec_word_min_count = form.cleaned_data['word2vec_word_min_count']
            start_date = form.cleaned_data['start_date']

            t = threading.Thread(target=train_model,
                            args=(0,start_date,number_of_clusters,word2vec_vector_size,word2vec_window_size,word2vec_word_min_count),
                            )
            t.setDaemon(True)
            t.start()
            #train_model(1,start_date,number_of_clusters,word2vec_vector_size,word2vec_window_size,word2vec_word_min_count)
            
            return HttpResponseRedirect(reverse('model_results'))
        else:
            return render(request, 'mainapp/train_model.html', {'form': form})

    else:
        form = TrainModelForm()
    return render(request, 'mainapp/train_model.html', {'form': form})

class ML_recordListView(LoginRequiredMixin,UserPassesTestMixin,generic.ListView):
    model = ML_record
    context_object_name = 'ML_record_list'
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.is_staff
