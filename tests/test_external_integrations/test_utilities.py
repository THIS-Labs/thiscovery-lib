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


class TestOther(test_utils.BaseTestCase):
    def test_non_prod_env_url_param(self):
        test_env = utils.namespace2name(UNIT_TEST_NAMESPACE)
        expected_result = f"&env={test_env}"
        result = utils.non_prod_env_url_param()
        self.assertEqual(expected_result, result)


class TestCreateAnonymousUrlParams(test_utils.BaseTestCase):
    def test_correct_output_external_task_id_none(self):
        expected_result = (
            "?anon_project_specific_user_id=a0c2668e-60ae-45fc-95e6-50270c0fb6a8"
            "&first_name=Egg"
            "&anon_user_task_id=e142fdf0-dea3-4513-9226-a1134037f57f"
            "&project_task_id=744edca2-190e-4753-ae2c-7223bc2f8892"
        )
        result = utils.create_anonymous_url_params(
            base_url="www.eggs.com",
            anon_project_specific_user_id="a0c2668e-60ae-45fc-95e6-50270c0fb6a8",
            user_first_name="Egg",
            anon_user_task_id="e142fdf0-dea3-4513-9226-a1134037f57f",
            project_task_id="744edca2-190e-4753-ae2c-7223bc2f8892",
            external_task_id=None,
        )
        self.assertEqual(expected_result, result)

    def test_correct_output_with_external_task_id(self):
        expected_result = (
            "?anon_project_specific_user_id=a0c2668e-60ae-45fc-95e6-50270c0fb6a8"
            "&first_name=Egg"
            "&anon_user_task_id=e142fdf0-dea3-4513-9226-a1134037f57f"
            "&project_task_id=744edca2-190e-4753-ae2c-7223bc2f8892"
            "&external_task_id=spam_eggs"
        )
        result = utils.create_anonymous_url_params(
            base_url="www.eggs.com",
            anon_project_specific_user_id="a0c2668e-60ae-45fc-95e6-50270c0fb6a8",
            user_first_name="Egg",
            anon_user_task_id="e142fdf0-dea3-4513-9226-a1134037f57f",
            project_task_id="744edca2-190e-4753-ae2c-7223bc2f8892",
            external_task_id="spam_eggs",
        )
        self.assertEqual(expected_result, result)

    def test_invalid_anon_project_specific_user_id_raises_error(self):
        with self.assertRaises(AssertionError) as err:
            utils.create_anonymous_url_params(
                base_url="www.eggs.com",
                anon_project_specific_user_id=None,
                user_first_name="Egg",
                anon_user_task_id="e142fdf0-dea3-4513-9226-a1134037f57f",
                project_task_id="744edca2-190e-4753-ae2c-7223bc2f8892",
                external_task_id="spam_eggs",
            )
        self.assertEqual("anon_project_specific_user_id is null", err.exception.args[0])

    def test_invalid_anon_user_task_id_raises_error(self):
        with self.assertRaises(AssertionError) as err:
            utils.create_anonymous_url_params(
                base_url="www.eggs.com",
                anon_project_specific_user_id="a0c2668e-60ae-45fc-95e6-50270c0fb6a8",
                user_first_name="Egg",
                anon_user_task_id=None,
                project_task_id="744edca2-190e-4753-ae2c-7223bc2f8892",
                external_task_id="spam_eggs",
            )
        self.assertEqual("anon_user_task_id is null", err.exception.args[0])

    def test_invalid_anon_project_specific_user_id_raises_error(self):
        with self.assertRaises(AssertionError) as err:
            utils.create_anonymous_url_params(
                base_url="www.eggs.com",
                anon_project_specific_user_id="a0c2668e-60ae-45fc-95e6-50270c0fb6a8",
                user_first_name="Egg",
                anon_user_task_id="e142fdf0-dea3-4513-9226-a1134037f57f",
                project_task_id="",
                external_task_id="spam_eggs",
            )
        self.assertEqual("project_task_id is null", err.exception.args[0])


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


class TestExceptions(test_utils.BaseTestCase):
    def test_DetailedValueError_init_ok_non_jsonable_payload(self):
        class MockHubSpotInvalidEmailResponse:
            content = b'{"validationResults":[{"isValid":false,"message":"Email address invalid.email@wales.nhs.ik is invalid",'
            b'"error":"INVALID_EMAIL","name":"email"}],"status":"error","message":"Property values were not valid",'
            b'"correlationId":"70a021f3-0224-4ea9-bfab-d6374d4d7e68"}'
            status_code = 400
            url = "https://api.hubapi.com/contacts/v1/contact/createOrUpdate/email/invalid.email@wales.nhs.ik"

        mock_response = MockHubSpotInvalidEmailResponse()
        errorjson = {
            "url": mock_response.url,
            "result": mock_response,  # this is the problematic bit of errorjson
            "content": mock_response.content,
        }

        try:
            raise utils.DetailedValueError(
                "Hubspot call returned HTTP code " + str(mock_response.status_code),
                errorjson,
            )
        except Exception as ex:
            error_message = str(ex)
            self.assertEqual(
                "DetailedValueError failed to decode error details; here is the error message: Hubspot call returned HTTP code 400",
                error_message,
            )


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
