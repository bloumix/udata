# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from urlparse import urlparse

from flask import current_app

from .backends import get as get_linkchecker, NoCheckLinkchecker


def _get_check_keys(the_dict, resource, previous_status):
    check_keys = {k: v for k, v in the_dict.iteritems()
                  if k.startswith('check:')}
    check_keys['check:count-availability'] = _compute_count_availability(
            resource, check_keys.get('check:available'), previous_status)
    return check_keys


def _compute_count_availability(resource, status, previous_status):
    '''Compute the `check:count-availability` extra value'''
    count_availability = resource.extras.get('check:count-availability', 1)
    return count_availability + 1 if status == previous_status else 1


def is_ignored(resource):
    '''Check of the resource's URL is part of LINKCHECKING_IGNORE_DOMAINS'''
    ignored_domains = current_app.config['LINKCHECKING_IGNORE_DOMAINS']
    url = resource.url
    if url:
        parsed_url = urlparse(url)
        return parsed_url.netloc in ignored_domains
    return True


def dummy_check_response():
    '''Trigger a dummy check'''
    return NoCheckLinkchecker().check(None)


def check_resource(resource):
    '''
    Check a resource availability against a linkchecker backend

    The linkchecker used can be configured on a resource basis by setting
    the `resource.extras['check:checker']` attribute with a key that points
    to a valid `udata.linkcheckers` entrypoint. If not set, it will
    fallback on the default linkchecker defined by the configuration variable
    `LINKCHECKING_DEFAULT_LINKCHECKER`.

    Returns
    -------
    dict or (dict, int)
        Check results dict and status code (if error).
    '''
    linkchecker_type = resource.extras.get('check:checker')
    LinkChecker = get_linkchecker(linkchecker_type)
    if not LinkChecker:
        return {'error': 'No linkchecker configured.'}, 503
    if is_ignored(resource):
        return dummy_check_response()
    result = LinkChecker().check(resource)
    if not result:
        return {'error': 'No response from linkchecker'}, 503
    elif result.get('check:error'):
        return {'error': result['check:error']}, 500
    elif not result.get('check:status'):
        return {'error': 'No status in response from linkchecker'}, 503
    # store the check result in the resource's extras
    # XXX maybe this logic should be in the `Resource` model?
    previous_status = resource.extras.get('check:available')
    check_keys = _get_check_keys(result, resource, previous_status)
    resource.extras.update(check_keys)
    resource.save()
    return result
