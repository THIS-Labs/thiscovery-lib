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
import local.dev_config  # sets env variables TEST_ON_AWS and AWS_TEST_API
import local.secrets  # sets env variables THISCOVERY_AFS25_PROFILE and THISCOVERY_AMP205_PROFILE
import thiscovery_lib.utilities as utils
from unittest import TestCase

import thiscovery_dev_tools.testing_tools as test_utils

from local.dev_config import UNIT_TEST_NAMESPACE
from http import HTTPStatus


class TestValidateInt(TestCase):
    def test_validate_int_ok(self):
        from thiscovery_lib.utilities import validate_int

        # self.assertTrue(validate_int, 6)
        i = 7
        self.assertEqual(i, validate_int(i))

    def test_validate_int_fail(self):
        from thiscovery_lib.utilities import validate_int, DetailedValueError

        self.assertRaises(DetailedValueError, validate_int, "abc")


class TestValidateUuid(TestCase):
    def test_validate_uuid_ok(self):
        import uuid
        from thiscovery_lib.utilities import validate_uuid

        uuid_str = str(uuid.uuid4())
        self.assertEqual(uuid_str, validate_uuid(uuid_str))

    def test_validate_uuid_fail_1(self):
        import uuid
        from thiscovery_lib.utilities import DetailedValueError, validate_uuid

        uuid_str = str(uuid.uuid1())
        self.assertRaises(DetailedValueError, validate_uuid, uuid_str)

    def test_validate_uuid_fail_string(self):
        from thiscovery_lib.utilities import DetailedValueError, validate_uuid

        uuid_str = "this is not a uuid"
        self.assertRaises(DetailedValueError, validate_uuid, uuid_str)


class TestValidateUtcDatetime(TestCase):
    def test_validate_utc_datetime_ok(self):
        from thiscovery_lib.utilities import validate_utc_datetime, now_with_tz

        dt = str(now_with_tz())
        self.assertEqual(dt, validate_utc_datetime(dt))

    def test_validate_utc_datetime_fail_us_date(self):
        from thiscovery_lib.utilities import validate_utc_datetime, DetailedValueError

        dt = "2018-23-06 13:40:13.242219"
        self.assertRaises(DetailedValueError, validate_utc_datetime, dt)

    def test_validate_utc_datetime_fail_time_only(self):
        from thiscovery_lib.utilities import validate_utc_datetime, DetailedValueError

        dt = "13:40:13.242219"
        self.assertRaises(DetailedValueError, validate_utc_datetime, dt)

    def test_validate_utc_datetime_fail_string(self):
        from thiscovery_lib.utilities import validate_utc_datetime, DetailedValueError

        dt = "this is not a datetime"
        self.assertRaises(DetailedValueError, validate_utc_datetime, dt)


class TestMinimiseWhiteSpace(TestCase):
    def test_minimise_white_space_change(self):
        from thiscovery_lib.utilities import minimise_white_space

        str1 = """hello
            world      world"""
        str2 = "hello world world"
        self.assertEqual(str2, minimise_white_space(str1))

    def test_minimise_white_space_nochange(self):
        from thiscovery_lib.utilities import minimise_white_space

        str1 = "hello world world"
        str2 = "hello world world"
        self.assertEqual(str2, minimise_white_space(str1))


@utils.lambda_wrapper
@utils.api_error_handler
def raise_exception(event: dict, exception, *exception_args):
    raise exception(*exception_args)


class ApiErrorHandlerTestCase(test_utils.BaseTestCase):
    details_dict = dict()

    def test_deliberate_error_handling(self):
        result = raise_exception(
            dict(), utils.DeliberateError, "deliberate error message", self.details_dict
        )
        self.assertEqual(HTTPStatus.METHOD_NOT_ALLOWED, result["statusCode"])

    def test_duplicate_insert_error_handling(self):
        result = raise_exception(
            dict(),
            utils.DuplicateInsertError,
            "duplicate insert error message",
            self.details_dict,
        )
        self.assertEqual(HTTPStatus.CONFLICT, result["statusCode"])

    def test_object_does_not_exist_error_handling(self):
        result = raise_exception(
            dict(),
            utils.ObjectDoesNotExistError,
            "object does not exist error message",
            self.details_dict,
        )
        self.assertEqual(HTTPStatus.NOT_FOUND, result["statusCode"])

    def test_detailed_value_error_handling(self):
        result = raise_exception(
            dict(),
            utils.DetailedValueError,
            "detailed value error message",
            self.details_dict,
        )
        self.assertEqual(HTTPStatus.BAD_REQUEST, result["statusCode"])

    def test_assertion_error_handling(self):
        result = raise_exception(
            dict(),
            AssertionError,
            "assertion error message",
            self.details_dict,
        )
        self.assertEqual(HTTPStatus.INTERNAL_SERVER_ERROR, result["statusCode"])
