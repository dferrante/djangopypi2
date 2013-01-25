from django.conf.urls.defaults import patterns, url
from . import views

PACKAGE = r'(?P<package_name>[\w\d_\.\-]+)'
VERSION = r'(?P<version>[\w\d_\.\-]+)'

urlpatterns = patterns('',
    url('^$', views.index, name="djangopypi2-root"),

    url('^simple/$'                , views.simple_index   , name='djangopypi2-simple-index'),
    url('^simple/' + PACKAGE + '/$', views.simple_details , name='djangopypi2-simple-package-info'),
    url('^simple/' + PACKAGE + '/' + VERSION + '/$', views.simple_release_details , name='djangopypi2-simple-package-release-info'),

    url('^pypi/$'                                          , views.index          , name='djangopypi2-pypi-index'),
    url('^pypi/' + PACKAGE + '/$'                          , views.package_details, name='djangopypi2-pypi-package'),
    #url('^pypi/' + PACKAGE + '/' + VERSION + '/$'          , views.package_details, name='djangopypi2-pypi-package'),
    url('^pypi/' + PACKAGE + r'/doap\.rdf$'                , views.package_doap   , name='djangopypi2-pypi-package-doap'),
    url('^pypi/' + PACKAGE + '/' + VERSION + r'/doap\.rdf$', views.release_doap   , name='djangopypi2-pypi-release-doap'),
)
