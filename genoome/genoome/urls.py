from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.flatpages.views import flatpage
from django_markdown import flatpages

from accounts.views import LandingView
from disease.views import upload_progress

admin.autodiscover()
flatpages.register()

urlpatterns = patterns('',
    url(r'^$', LandingView.as_view(), name='landing_page'),
    url(r'^faq/$', TemplateView.as_view(template_name='faq.html'), name='faq'),
    url(r'^genotype-description', flatpage, name='genotype_description'),

    # Examples:
    # url(r'^$', 'genoome.views.home', name='home'),
    url(r'^update-progress/$', upload_progress, name='upload_progress'),
    url(r'^disease/', include('disease.urls', namespace='disease')),
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^payments/', include('payments.urls', namespace='payments')),

    url('^markdown/', include('django_markdown.urls')),


    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

# Uncomment the next line to serve media files in dev.
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
