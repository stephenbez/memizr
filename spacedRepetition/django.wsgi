import sys

sys.path.insert(0, '/home/steve/memizr')
sys.path.insert(0, '/home/steve/memizr/spacedRepetition')

import spacedRepetition.settings

import django.core.management
django.core.management.setup_environ(spacedRepetition.settings)
utility = django.core.management.ManagementUtility()
command = utility.fetch_command('runserver')

command.validate()

import django.conf
import django.utils

django.utils.translation.activate(django.conf.settings.LANGUAGE_CODE)

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
