from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns=[
    #path('signup',views.signup,name='signup'),
    path('', views.index, name='dashboard'),
    path('login',views.login_user,name='login'),
    path('success',views.success,name='success'),
    path('profile', views.profile, name='profile'),
    path('page_calender', views.calender, name='page_calender'),
    path('profile_account', views.profile_account, name='profile_account'),
    #path('siteupdate',views.siteupdate,name='siteupdate'),
    #path('editprofile',views.update_profile,name='editprofile'),
    #path('change_password', views.change_password, name='change_password'),
    #path('userclient',views.user_update, name='userclient'),
    path('test',views.test, name='test'),
    #path('user_registration', views.userre, name='user_registration'),
    path('company_registration', views.create_company, name='company_registration'),
    path('employee_registration', views.create_employee, name='employee_registration'),
    path('user', views.signup, name='user'),
    path('activates/<uidb64>/<token>/',views.activates, name='activates'),
    path('setpassword/<int:uid>',views.setpassword,name='setpassword'),
    path('companyview',views.companyview,name='companyview'),
    path('company_view',views.company_view,name='company_view'),
    path('company_detail/<int:id>/',views.company_detail,name='company_detail'),
    path('employeeview/<int:id>/',views.employeeview,name='employeeview'),
    path('employee_view',views.employee_view,name='employee_view'),
    path('employee_detail/<int:id>/',views.employee_detail,name='employee_detail'),
    path('updatecompany/<int:pk>',views.company_update, name='updatecompany'),
    path('deletecompany', views.company_delete, name='deletecompany'),
    path('companydelete/<int:id>/',views.company_delete,name='companydelete'),
    path('userview',views.userview,name='userview'),
    path('user_view',views.user_view,name='user_view'),
    path('employee_update/<int:emp_id>/<int:cmp_id>/',views.employee_update,name='employeeupdate'),
    path('employee_delete/<int:emp_id>/<int:cmp_id>/',views.employee_delete,name='employeedelete'),
    path('addgroup',views.addgroup,name='addgroup'),
    path('groupview',views.groupview,name='groupview'),
    path('group_view',views.group_view,name='group_view'),
    path('group_detail/<int:id>/',views.group_detail,name='group_detail'),
    path('user_delete/<int:id>/', views.user_delete, name='user_delete'),
    path('group_update/<int:id>',views.group_update,name='group_update'),
    path('group_delete/<int:id>',views.group_delete,name='group_delete'),
    path('clientupdate/<int:id>',views.client_update, name='clientupdate'),
    # path('dashboard/', views.dashboard_view,name = 'actuvity')


]