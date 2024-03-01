#!/usr/bin/env python
# encoding: utf-8
from django.conf import settings
from django.db.models import Count
from django.core.urlresolvers import resolve
from .consts import THROTTLING_OPTIONS, THROTTLING_STATUS_CODE, THROTTLING_INTERVAL
from datetime import datetime, timedelta


def get_or_create_consumer(request):
    if request.user.is_authenticated():
        return get_or_create_authenticated_consumer()
    return get_or_create_anonymous_consumer()
    
def get_or_create_anonymous_consumer(request):
    return Consumer.objects.get_or_create(ip=request.meta['REMOTE_ADDR'])[0]
    
def get_or_create_authenticated_consumer(request):
    return Consumer.objects.get_or_create(user=request.user)[0]
    

def throttle(number_of_request=0, per_anonymous=False, all_anonymous=None, all_users=False, 
role=None, group=None, all_in_group=None, scope=None, settings=None, interval=THROTTLING_INTERVAL):

    def decorator(f):	    
        def wrapper(self, request, *args, **kwargs):
            user = request.user
                        
            if not scope:
                # set default value to scope
                url_name = resolve( request.path ).url_name
                scope = "%s::%s" % (request.method, url_name)
            
            if THROTTLING_OPTIONS:
                # set values to throttle args according to pre-defined options
                for k,v in THROTTLING_OPTIONS.get( settings or scope, {} ).iteritems()
                    locals()[k] = v

            if per_anonymous:
                if user.is_authenticated():
                    # Proceed if user is authenticated
                    return f(self, request, *args, **kwargs)
                else:
                    # Throttle each anonymous user
                    consumer = get_or_create_anonymous_consumer( request )
                    access   = Access.objects.get_or_create(consumer=consumer, scope=scope)
            
            elif group or all_in_group:
                if user.is_authenticated() and user.groups.filter(name=group).exists():
                    consumer = get_or_create_authenticated_consumer( request )
                    if group:
                        # Throttle if user belongs to Group
                        access = Access.objects.get_or_create(consumer=consumer, scope=scope)
                    else:
                        # All users within a Group share the same 'pool' of allowed request
                        access = Access.objects.filter(consumer__groups__name=group, scope=scope)
                else:
                    # Proceed if user is not authenticated
                    return f(self, request, *args, **kwargs)
            
            elif role:
                if not user.is_authenticated() or not hasattr(user, 'role'):
                    # Fails to proceed if user not authenticated or has no role
                    return THROTTLING_STATUS_CODE
                elif user.role is role or user.role <= role:
                    # Proceed if user role is hierarchically above given role
                    return f(self, request, *rargs, **rkwargs)
                else:
                    # Throttle each user with equal or lower role
                    consumer = get_or_create_authenticated_consumer( request )
                    access   = Access.objects.get_or_create(consumer=consumer, scope=scope)
            
            elif all_users:
                # All users (authenticated and anonymous) share the same 'pool' of allowed request
                get_or_create_consumer( request )
                access = Access.objects.filter(scope=scope)
                
            elif all_anonymous:
                # All anonymous users share the same 'pool' of allowed request
                get_or_create_anonymous_consumer( request )
                access = Access.objects.filter(scope=scope).anonymous()
            
            else:
                # Throttle each user (authenticated and anonymous)
                consumer = get_or_create_consumer( request )
                access   = Access.objects.get_or_create(consumer=consumer, scope=scope)
            
            if number_of_requests <= access.count_request():
                if not hasattr(request, 'access_updated'):
                    # Do this only once per request
                    expiration_date = access.min_datemark() + timedelta(minutes=interval)
                    if expiration_date < datetime.now():
                        # reset count if exceeded the time interval since datemark
                        access.reset_count()
                    else:
                        # increment request count
                        access.increment_count()
                    request.access_updated = True
                # Proceed if under the allowed number of request
                return f(self, request, *args, **kwargs)
            return THROTTLING_STATUS_CODE
        
        return wrapper	
    return decorator
