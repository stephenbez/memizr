from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^spacedRepetition/', include('spacedRepetition.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^$', 'spacedRepetition.flashcards.views.home'),
    (r'^review/$', 'spacedRepetition.flashcards.views.review'),
    (r'^add/$', 'spacedRepetition.flashcards.views.add'),
    (r'^addCard/$', 'spacedRepetition.flashcards.views.addCard'),
    (r'^grade/$', 'spacedRepetition.flashcards.views.grade'),
    (r'^edit/$', 'spacedRepetition.flashcards.views.edit'),
    (r'^editCardSubmit/$', 'spacedRepetition.flashcards.views.editCardSubmit'),
    (r'^edit/(?P<card_id>\d+)/$', 'spacedRepetition.flashcards.views.editCard'),
    (r'^delete/$', 'spacedRepetition.flashcards.views.delete'), 
    (r'^export/$', 'spacedRepetition.flashcards.views.export'), 
    (r'^import/$', 'spacedRepetition.flashcards.views.import_cards'), 
    (r'^upload/$', 'spacedRepetition.flashcards.views.upload'), 
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_DOC_ROOT}),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page' : '/'}),
    (r'^accounts/register/$', 'spacedRepetition.flashcards.views.register'),
)

