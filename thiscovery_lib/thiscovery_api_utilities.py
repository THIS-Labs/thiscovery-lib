#
#   Thiscovery API - THIS Institute’s citizen science platform
#   Copyright (C) 2019 THIS Institute
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   A copy of the GNU Affero General Public License is available in the
#   docs folder of this project.  It is also available www.gnu.org/licenses/
#
import functools
import json
from http import HTTPStatus

import thiscovery_lib.utilities as utils


class ThiscoveryApiClient:

    def __init__(self, correlation_id=None, env_override=None, api_prefix=''):
        self.correlation_id = correlation_id
        self.logger = utils.get_logger()
        if api_prefix:
            api_prefix += '-'
        if env_override:
            env_name = env_override
        else:
            env_name = utils.get_environment_name()
        if env_name == 'prod':
            self.base_url = f'https://{api_prefix}api.thiscovery.org/'
        else:
            self.base_url = f'https://{env_name}-{api_prefix}api.thiscovery.org/'


def check_response(expected_status_code):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            assert response['statusCode'] == expected_status_code, \
                f'API call initiated by {func.__module__}.{func.__name__} ' \
                f'returned error: {response}'
            return response
        return wrapper
    return decorator


def process_response(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        return json.loads(response['body'])
    return wrapper

