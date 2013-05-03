from django.conf.urls import patterns, include, url
from ArbiSms import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^projects/$','sms.views.projects'),
    url(r'^projects/spiders$','sms.views.spiders'),
    url(r'^projects/jobs$','sms.views.jobs'),
    url(r'^$', 'sms.views.main'),
    url(r'^login$', 'sms.views.login_view'),
    url(r'^logout$', 'sms.views.logout_view'),
    url(r'^signup$', 'sms.views.signup'),
    url(r'^submit$', 'sms.views.add_server'),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
                        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
                         {'document_root' : settings.STATIC_ROOT, 'show_indexes': True}
                        ),
                        )