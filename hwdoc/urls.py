# -*- coding: utf-8 -*- vim:encoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab
from django.conf.urls.defaults import *

urlpatterns = patterns('servermon.hwdoc.views',
            (r'^project/(?P<project_id>[\d]+)/$', 'project'),
            (r'^equipment/(?P<equipment_id>[\d]+)/$', 'equipment'),
            (r'^search/$', 'search'),
            (r'^advancedsearch/$', 'advancedsearch'),
            )
