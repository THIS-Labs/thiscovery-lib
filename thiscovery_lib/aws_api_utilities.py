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


def check_response(*expected_status_codes):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            assert (
                response["ResponseMetadata"]["HTTPStatusCode"] in expected_status_codes
            ), (
                f"Boto3 API call initiated by {func.__module__}.{func.__name__} "
                f"returned error: {response}"
            )
            return response

        return wrapper

    return decorator
