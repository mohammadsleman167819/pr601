from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser,Company,Employee,Course,Job_Post,ML_record



class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["email", "username","role"]

admin.site.register(CustomUser, CustomUserAdmin)


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name','city','phone')
    

admin.site.register(Company, CompanyAdmin)


class EmployeeAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Basic Info', {
            'fields': ('firstname', 'lastname', 'dateOfBirth','city','phone')
        }),
        ('Resume', {
            'fields': ('education', 'experience','awards','hobbies','skills','references','other')
        }),
        (None,{
            'fields':('cluster',)
        }),
    )

admin.site.register(Employee, EmployeeAdmin)

class Job_PostAdmin(admin.ModelAdmin):
    list_display = ('job_title','company_id')
    list_filter  = ('company_id',)

admin.site.register(Job_Post, Job_PostAdmin)

class CourseAdmin(admin.ModelAdmin):
    list_display = ('courseTitle','company_id')
   
admin.site.register(Course, CourseAdmin)

