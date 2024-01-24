# Encoding: utf-8

# --
# Copyright (c) 2008-2024 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import routes
from webob.exc import HTTPNotFound

from nagare.services import plugin


class Router(plugin.Plugin):
    """A service wrapped around the router.

    Being now a service, the router can be injected
    """

    @staticmethod
    def create_dispatch_args(request, response, **params):
        return request.path_info, request.method, request, response

    def __call__(self, o, url, method, request, response, *args):
        mapper = getattr(o, 'nagare_urls_mapper', None)
        if mapper is None:
            raise HTTPNotFound(url)

        match_dict = mapper.match('/' + url.strip('/'), {'REQUEST_METHOD': method, 'request': request})
        if match_dict is None:
            raise HTTPNotFound(url)

        args += (url, method, request, response)
        return match_dict.pop('action')(o, *args, **match_dict)


def route_for(cls, url='', methods=('GET', 'HEAD'), validate=None, **kw):
    """The routing decorator."""

    def _(f):
        cls.nagare_urls_mapper = getattr(cls, 'nagare_urls_mapper', None) or routes.Mapper(register=False)

        conditions = {}
        if methods:
            conditions['method'] = [methods] if isinstance(methods, str) else methods

        if validate:
            conditions['function'] = lambda params, match_dict: validate(params['request'], match_dict)

        cls.nagare_urls_mapper.connect(None, '/' + url.strip('/'), action=f, conditions=conditions, **kw)

        return f

    return _
