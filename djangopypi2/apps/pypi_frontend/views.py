from django.http import Http404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.views.generic import list_detail
from ..pypi_ui.shortcuts import render_to_response
from ..pypi_packages.models import Package
from ..pypi_packages.models import Release
from .models import MirrorSite
from . import xmlrpc_views
from . import distutils_request
from . import distutils_views

@csrf_exempt
def index(request):
    """ Root view of the package index, handle incoming actions from distutils
    or redirect to a more user friendly view """
    if xmlrpc_views.is_xmlrpc_request(request):
        return xmlrpc_views.handle_xmlrpc_request(request)

    if distutils_request.is_distutils_request(request):
        return distutils_request.handle_distutils_request(request)

    return HttpResponseRedirect(reverse('djangopypi2-packages-index'))

def simple_index(request):
    return list_detail.object_list(
        request,
        template_name        = 'pypi_frontend/package_list_simple.html',
        template_object_name = 'package',
        queryset             = Package.objects.all(),
    )

def _mirror_if_not_found(proxy_folder):
    def decorator(func):
        def internal(request, package_name, version=None):
            try:
                return func(request, package_name, version)
            except Http404:
                is_cached = distutils_views.cache_pypi_package(request, package_name, version)
                if is_cached: #got it, try again
                    try:
                        return func(request, package_name, version)
                    except Http404: #fuck it
                        pass

                for mirror_site in MirrorSite.objects.filter(enabled=True):
                    url = '/'.join([mirror_site.url.rstrip('/'), proxy_folder, package_name])
                    mirror_site.logs.create(action='Redirect to ' + url)
                    return HttpResponseRedirect(url)
            raise Http404(u'%s is not a registered package' % (package_name,))
        return internal
    return decorator

@_mirror_if_not_found('simple')
def simple_details(request, package_name, version=None):
    try:
        package = Package.objects.get(name__iexact=package_name)
    except Package.DoesNotExist:
        package = get_object_or_404(Package, name__iexact=package_name.replace('_', '-'))
    # If the package we found is not exactly the same as the name the user typed, redirect
    # to the proper url:
    if package.name != package_name:
        return HttpResponseRedirect(reverse('djangopypi2-simple-package-info', kwargs=dict(package_name=package.name)))
    return render_to_response('pypi_frontend/package_detail_simple.html',
                              context_instance=RequestContext(request, dict(package=package)),
                              mimetype='text/html')

@_mirror_if_not_found('simple')
def simple_release_details(request, package_name, version):
    try:
        release = Release.objects.get(package__name__iexact=package_name, version=version)
    except Release.DoesNotExist:
        release = get_object_or_404(Release, package__name__iexact=package_name.replace('_', '-'), version=version)
    package = release.package
    # If the package we found is not exactly the same as the name the user typed, redirect
    # to the proper url:
    if package.name != package_name:
        return HttpResponseRedirect(reverse('djangopypi2-simple-package-release-info', kwargs=dict(package_name=package.name, version=version)))
    return render_to_response('pypi_frontend/package_detail_simple.html',
                              context_instance=RequestContext(request, dict(package=package)),
                              mimetype='text/html')

@_mirror_if_not_found('pypi')
def package_details(request, package_name, version=None):
    package = get_object_or_404(Package, name=package_name)
    return HttpResponseRedirect(package.get_absolute_url())

@_mirror_if_not_found('pypi')
def package_doap(request, package_name):
    package = get_object_or_404(Package, name=package_name)
    return render_to_response('pypi_frontend/package_doap.xml',
                              context_instance=RequestContext(request, dict(package=package)),
                              mimetype='text/xml')

def release_doap(request, package_name, version):
    release = get_object_or_404(Release, package__name=package_name, version=version)
    return render_to_response('pypi_frontend/release_doap.xml',
                              context_instance=RequestContext(request, dict(release=release)),
                              mimetype='text/xml')
