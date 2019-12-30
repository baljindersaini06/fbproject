from django.contrib.auth.models import Permission
from django.contrib import admin
from fbcampaign.models import User,SiteConfiguration,SmtpConfiguration, Company, Employee
admin.site.register(Permission)
# Register your models here.
admin.site.register(User)
admin.site.register(SiteConfiguration)
admin.site.register(SmtpConfiguration)
admin.site.register(Company)
admin.site.register(Employee)