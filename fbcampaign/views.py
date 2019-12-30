from django.shortcuts import render, reverse, redirect, get_object_or_404
from .models import *
from .forms import (
    UserCreateForm, LoginForm, PasswordChangedForm, UserForm,SmtpForm,SiteForm, 
    ImageForm,UpdateSiteForm, SignUpForm, SetPasswordForm, CompanyForm, EmployeeForm,
    UpdateEmployee, GroupForm, GroupUpdateForm)
   
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.template.response import TemplateResponse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
User = get_user_model()
from fbcampaign.models import SiteConfiguration,SmtpConfiguration, Company, Employee
from django_otp.decorators import otp_required
from two_factor.models import PhoneDevice
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from .tokens import account_activation_token
from django.core.mail import EmailMessage, send_mail
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User,Group
from django.contrib.auth import get_user_model
User = get_user_model()
from django.utils import six
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import permission_required
import json
from django.views.generic.edit import DeleteView
from django.contrib.auth.models import Permission

from django.contrib.admin.models import LogEntry


def group_required(group, login_url=None, raise_exception=False):
    """
    Decorator for views that checks whether a user has a group permission,
    redirecting to the log-in page if necessary.
    If the raise_exception parameter is given the PermissionDenied exception
    is raised.
    """
    def check_perms(user):
        if isinstance(group, six.string_types):
            groups = (group, )
        else:
            groups = group
        # First check if the user has the permission (even anon users)

        if user.groups.filter(name__in=groups).exists():
            return True
        # In case the 403 handler should be called raise the exception
        if raise_exception:
            raise PermissionDenied
        # As the last resort, show the login form
        return False
    return user_passes_test(check_perms, login_url='profile')





# def signup(request):
#     if request.method == 'POST':
#         form = UserCreateForm(request.POST)
#         if form.is_valid():
#             user= form.save(commit=False)
#             user.save()
#             return redirect('dashboard')

#     else:
#         form = UserCreateForm()
#     return render(request, 'auth/user_form.html', {'form': form})

@login_required
def signup(request):
    a=Group.objects.all()
    if request.method == 'POST':
        print("hello")
        form = SignUpForm(request.POST)
        if form.is_valid():
            print("hi")
            user= form.save(commit=False)
            user.phone_no = form.cleaned_data.get('phone_no')
            user.is_active = False
            user.save()
            role = form.cleaned_data.get('role')
            group = Group.objects.get(name=role)
            user.groups.add(group)
            current_site = get_current_site(request)
            mail_subject = 'Activate your Account.'
            message = render_to_string('account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)) ,
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
          
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')
    else:      
        form = SignUpForm()
        
    return render(request, 'registration/user_registration.html', {'form': form,'a':a})



def activates(request, uidb64, token, backend='django.contrib.auth.backends.ModelBackend'):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return HttpResponseRedirect(reverse('setpassword',args=(uid,)))
    else:
        return HttpResponse('Activation link is invalid!')


def setpassword(request,uid, backend='django.contrib.auth.backends.ModelBackend'):
    if request.method=='POST':
        form = SetPasswordForm(request.POST)
        if form.is_valid():
            user = User.objects.get(pk=uid)
            password = request.POST.get('password')
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('/')
    else:
        form = SetPasswordForm()
    return render(request,"passwordset.html",{'form':form})


#@otp_required
@login_required
def index(request):
    try:
        a=PhoneDevice.objects.filter(user=request.user)
        if a:
            return render(request, 'fbcampaign/index.html')
        else:
            return render(request, 'fbcampaign/index.html')

    except PhoneDevice.DoesNotExist:
        a = None


@login_required
def profile(request):
    return render(request, 'fbcampaign/profile.html')


@login_required
def calender(request):
    return render(request, 'fbcampaign/page_calender.html')

def login_user(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request,username=username, password=password)          
            if user is not None:
                if user.is_active:
                    login(request, user)    
                    return redirect('/')
                    
    else:
        login_form = LoginForm()
    return render(request, 'registration/login.html', {'login_form': login_form,})


def success(request):
    return render(request, 'fbcampaign/success.html')


@login_required
def profile_account(request):
    password_form = PasswordChangedForm(request.POST)
    profile_form = UserForm(request.POST)
    image_form = ImageForm(request.POST)
    site_form = SiteForm()
    smtp_form = SmtpForm()

    try:
        site_set=SiteConfiguration.objects.get(user=request.user) 
    except SiteConfiguration.DoesNotExist:
        site_set = None

    try:
        smtp_set=SmtpConfiguration.objects.get(user=request.user)
    except SmtpConfiguration.DoesNotExist:
        smtp_set = None

    if request.method == "POST":
        old_password = request.POST.get("old_password")
        if 'btnform2' in request.POST:
            password_form = PasswordChangedForm(request.user, request.POST)
            if request.POST.get("old_password"):
                user = User.objects.get(username= request.user.username)
                if user.check_password('{}'.format(old_password)) == False:
                    password_form.set_old_password_flag()
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Important!
                messages.success(request, 'Your password was successfully updated!')
                return HttpResponseRedirect(reverse('profile_account'))
            else:
                messages.error(request, 'Please correct the error below.')
        elif 'btnform1' in request.POST:
            profile_form = UserForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
        elif 'btnform3' in request.POST:
            image_form = ImageForm(request.POST, request.FILES , instance=request.user)
            if (image_form.is_valid()):
                image_form.save()            
                return HttpResponseRedirect(reverse('profile_account'))
        elif 'btnform4' in request.POST:
            if SiteConfiguration.objects.filter(user=request.user).exists():
                try:
                    site_sett=SiteConfiguration.objects.get(user=request.user) 
                except SiteConfiguration.DoesNotExist:
                    site_sett = None
                site_form = SiteForm(request.POST, request.FILES , instance=site_sett)        
                if site_form.is_valid():
                    site_form.save()            
                    return HttpResponseRedirect(reverse('profile_account'))                     
            else:       
                site_form = SiteForm(request.POST, request.FILES)
                if site_form.is_valid():
                    post = site_form.save(commit=False)
                    post.user = request.user
                    post.save()  
                    messages.success(request, 'Your site settings are successfully added !')
                    return HttpResponseRedirect(reverse('profile_account'))  
    
        elif 'btnform5' in request.POST:
            if SmtpConfiguration.objects.filter(user=request.user).exists(): 
                try:
                    smtp_sett=SmtpConfiguration.objects.get(user=request.user)
                except SmtpConfiguration.DoesNotExist:
                    smtp_sett = None              
                smtp_form = SmtpForm(request.POST, request.FILES , instance=smtp_sett)        
                if smtp_form.is_valid():
                    smtp_form.save()            
                    return HttpResponseRedirect(reverse('profile_account'))                      
            else:       
                smtp_form = SmtpForm(request.POST, request.FILES)
                if smtp_form.is_valid():
                    smtp_post = smtp_form.save(commit=False)
                    smtp_post.user = request.user
                    smtp_post.save()  
                    messages.success(request, 'Your smtp settings are successfully added !')
                    return HttpResponseRedirect(reverse('profile_account'))     
        else:
            raise Http404
    else:
        if SiteConfiguration.objects.filter(user=request.user).exists():
            site_profile_form = SiteForm(instance=SiteConfiguration.objects.get(user=request.user)) 
        elif SmtpConfiguration.objects.filter(user=request.user).exists():
            smtp_form = SmtpForm(instance=SmtpConfiguration.objects.get(user=request.user))        

    return TemplateResponse(request, template="fbcampaign/extra_profile_account.html", context={
        'password_form': password_form,
        'profile_form': profile_form,
        'site_form': site_form,
        'smtp_form': smtp_form,
        'image_form': image_form,
        'site_set':site_set,
        'smtp_set':smtp_set,
    })


def test(request):
  response_str = "false"
  if request.is_ajax():
    old_password = request.GET.get("old_password")
    request_user = User.objects.get(id=request.user.id)
    if(request_user.check_password(old_password) == True):
        response_str = "true"
    return HttpResponse(response_str)

@login_required
@user_passes_test(lambda u: u.is_superuser)
@group_required(('HR', 'Admin','Accountant'))
def create_company(request):
    if request.method == "POST":
        form1 = CompanyForm(request.POST, request.FILES)
        if form1.is_valid():
            print("hello")
            form1.save()
            return HttpResponseRedirect(reverse('dashboard'))

    else:
        form1 = CompanyForm()
    return render(request, 'registration/company_registration.html', {'form1': form1})

@login_required
@user_passes_test(lambda u: u.is_superuser)
@group_required(('HR','Admin'))
def create_employee(request):
    com = Company.objects.all()

    if request.method == "POST":
        form2 = EmployeeForm(request.POST)
        if form2.is_valid():
            print("hello")
            form2.save()
            return HttpResponseRedirect(reverse('dashboard'))

    else:
        form2 = EmployeeForm()
    return render(request, 'registration/employee_registration.html', {'form2': form2,'com':com})


  
# def user_update(request):
#     return render(request, 'myapp/profile.html')

# def siteupdate(request):
#     if Site.objects.filter(user=username).exists():
#     if request.method == 'POST':
#         site_profile_form = UpdateSiteForm(request.POST, request.FILES , instance=request.user.site)
        
#         if site_profile_form.is_valid():
           
#             site_profile_form.save()            
#             return HttpResponseRedirect(reverse('success'))
        
#     else:
#         site_profile_form = UpdateSiteForm(instance=request.user)
#     return render(request, 'profile_tabs/updatesite.html', {
#         'site_profile_form': site_profile_form,
       
#     })


# @login_required
# def update_profile(request):
#     if request.method == 'POST':
#         user_form = ImageForm(request.POST, request.FILES , instance=request.user)
        
#         if (user_form.is_valid()):
           
#             user_form.save()            
#             return HttpResponseRedirect(reverse('profile_account'))
        
#     else:
#         user_form = ImageForm(instance=request.user)
#     return render(request, 'profile_tabs/change_avtar.html', {
#         'user_form': user_form
#     })


# @login_required
# def user_update(request, template_name='myapp/extra_profile_account.html'):
#     # user= get_object_or_404(User)
#     print("Helloo")
#     fform = UserForm(request.POST, instance=request.user)
#     if fform.is_valid():
#         fform.save()
#         return redirect('profile_account')
#     return render(request, template_name, {'fform':fform})

def companyview(request):
    test_all = Company.objects.all().values('id','company_name', 'description', 'company_website', 'company_address', 'company_location', 'company_pincode')
    data={"data": list(test_all)}
    with open('static/company.json', 'w') as f:
        json.dump(data, f, indent=4)
    return redirect('company_view')
   
   
def company_view(request):
    return render(request, 'fbcampaign/company_list.html')


def userview(request):
    test_all = User.objects.all().values('id','first_name','last_name', 'username', 'email', 'phone_no', 'groups')
    data={"data": list(test_all)}
    with open('static/user.json', 'w') as f:
        json.dump(data, f, indent=4)
    return redirect('user_view')

def user_view(request):
    return render(request, 'fbcampaign/user_list.html')


def user_delete(request,id):
    print("delete")
    c = User.objects.get(id=id)
    print(c)
    c.delete()    
    messages.success(request, "The user is deleted")  
    return HttpResponseRedirect(reverse('userview'))


def company_detail(request,id):
    compdetail=Company.objects.get(id=id)
    log = LogEntry.objects.select_related().all().order_by("id")
    return render(request, 'fbcampaign/company_detail.html',{'compdetail':compdetail,'log': log})


def employeeview(request,id):
    test_all = Employee.objects.filter(company_name=id).values('id','company_name', 'employee_name', 'phone_number', 'designation', 'employee_email', 'note')
    data={"data": list(test_all)}
    with open('static/employee.json', 'w') as f:
        json.dump(data, f, indent=4)
    return redirect('employee_view')
   
   
def employee_view(request):
    return render(request, 'fbcampaign/employee_list.html')


def employee_detail(request,id):
    empdetail=Employee.objects.get(id=id)
    return render(request, 'fbcampaign/employee_detail.html',{'empdetail':empdetail})


def company_update(request, pk, template_name='fbcampaign/edit_company2.html'):
    company= get_object_or_404(Company, pk=pk)
    form = CompanyForm(request.POST or None, instance=company)
    if form.is_valid():
        form.save()
        return redirect('companyview')
    return render(request, template_name, {'form':form, 'company':company})


# def company_delete(request, pk):
#     print("start delete")
#     company = get_object_or_404(Company, pk=pk, instance=company)
#     company.delete()
#     messages.success(request, "Company successfully deleted!")

#     return HttpResponseRedirect("companyview")

def company_delete(request,id):
    b = Company.objects.get(id=id)
    print(b)
    b.delete()    
    messages.success(request, "The user is deleted")  
    return HttpResponseRedirect(reverse('companyview'))


def client_update(request, id):
    client=User.objects.get(id=id)
    print(client)
    if request.method == 'POST':
        client_form = UserForm(request.POST, instance=client)
        if client_form.is_valid():
            client_form.save()
            return HttpResponseRedirect(reverse('userview'))
    else:
        client_form = UserForm(instance=client)
    return render(request, 'registration/client_update.html', {
        'client_form': client_form, 'client': client
        })


@login_required
def employee_update(request,emp_id,cmp_id):
    employee=Employee.objects.get(id=emp_id)
    if request.method == 'POST':
        user_form = UpdateEmployee(request.POST, instance=employee)
        if (user_form.is_valid()):
            user_form.save()            
            return HttpResponseRedirect(reverse('employeeview',args=(cmp_id,))) 
    else:
        user_form = UpdateEmployee(instance=employee)
    return render(request, 'registration/employee_update1.html', {
        'user_form': user_form,'employee':employee,
    })


def employee_delete(request,emp_id,cmp_id):

        b = Employee.objects.get(id=emp_id)
        b.delete()    
        messages.success(request, "The user is deleted")  
        return HttpResponseRedirect(reverse('employeeview',args=(cmp_id,)))

def addgroup(request):
    permissions = Permission.objects.all()
    if request.method == 'POST':
        addgroup_form = GroupForm(request.POST)
        if addgroup_form.is_valid:
            name = request.POST.get('name')
            permissions = request.POST.getlist('permissions')
            print(permissions)
            new_group = Group.objects.create(name =name)       
            for z in permissions:   
                new_group.permissions.add(z) 
                new_group.save()

    else:
        addgroup_form = GroupForm()
    return render(request, 'fbcampaign/addgroup.html', {'addgroup_form': addgroup_form,'permissions':permissions})


def groupview(request):
    test_all = Group.objects.all().values('id','name')
    data={"data": list(test_all)}
    with open('static/group.json', 'w') as f:
        json.dump(data, f, indent=4)
    return redirect('group_view')
   
   
def group_view(request):
    return render(request, 'fbcampaign/group_list.html')


def group_detail(request,id):
    groupdetail=Group.objects.get(id=id)
    grpper=groupdetail.permissions.all()
    # grpper1=groupdetail.permissions.all().count()
    # grpper1=grpper1+1
    return render(request, 'fbcampaign/group_detail.html',{'groupdetail':groupdetail,'grpper':grpper})



@login_required
def group_update(request,id):
    permissions = Permission.objects.all()
    groupupdate=Group.objects.get(id=id)
    grppermissions=groupupdate.permissions.all()
    if request.method == 'POST':
        group_form = GroupUpdateForm(request.POST, instance=groupupdate)
        if (group_form.is_valid()):
            group_form.save()            
            return HttpResponseRedirect(reverse('groupview')) 
    else:
        group_form = GroupUpdateForm(instance=groupupdate)
    return render(request, 'fbcampaign/update_group.html', {
        'group_form': group_form,'groupupdate':groupupdate,'permissions':permissions,'grppermissions':grppermissions
    })


def group_delete(request,id):

        b = Group.objects.get(id=id)
        b.delete()    
        messages.success(request, "group is deleted")  
        return HttpResponseRedirect(reverse('groupview'))
