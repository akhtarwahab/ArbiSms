from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'sms.views.index'),
    url(r'^login$', 'sms.views.login_view'),
    url(r'^logout$', 'sms.views.logout_view'),
    url(r'^signup$', 'sms.views.signup'),
    url(r'^ribbits$', 'sms.views.public'),
    url(r'^submit$', 'sms.views.submit'),
    url(r'^users/$', 'sms.views.users'),
    url(r'^users/(?P<username>\w{0,30})/$', 'sms.views.users'),
    url(r'^follow$', 'sms.views.follow'),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
