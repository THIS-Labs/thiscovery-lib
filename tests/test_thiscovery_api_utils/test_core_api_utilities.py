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

import json
import random
import string
import thiscovery_dev_tools.testing_tools as test_utils

from http import HTTPStatus
from pprint import pprint
from thiscovery_lib.core_api_utilities import CoreApiClient
from thiscovery_lib.utilities import get_environment_name


class TestCoreApiUtilities(test_utils.BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.core_client = CoreApiClient(get_environment_name())

    def test_get_user_by_user_id_ok(self):
        result = self.core_client.get_user_by_user_id(
            "1cbe9aad-b29f-46b5-920e-b4c496d42515"
        )
        expected_user = {
            "auth0_id": None,
            "avatar_string": "EE",
            "country_code": "GB",
            "country_name": "United Kingdom",
            "created": "2018-08-17T12:10:56.884543+00:00",
            "crm_id": None,
            "email": "eddie@email.co.uk",
            "first_name": "Eddie",
            "has_demo_project": True,
            "has_live_project": True,
            "id": "1cbe9aad-b29f-46b5-920e-b4c496d42515",
            "last_name": "Eagleton",
            "modified": "2018-11-02T11:07:33.785406+00:00",
            "status": None,
            "title": "Mr",
            "last_login": "2018-08-17T12:10:56.833885+00:00",
        }
        expected_status_code = HTTPStatus.OK
        self.assertDictEqual(expected_user, json.loads(result["body"]))
        self.assertEqual(expected_status_code, result["statusCode"])

    def test_get_user_by_user_id_not_found(self):
        result = self.core_client.get_user_by_user_id(
            "1cbe9aad-b29f-46b5-920e-b4c496d42516"
        )
        self.assertEqual(HTTPStatus.NOT_FOUND, result["statusCode"])

    def test_get_user_by_email_ok(self):
        result = self.core_client.get_user_by_email(email="delia@email.co.uk")
        self.assertEqual("35224bd5-f8a8-41f6-8502-f96e12d6ddde", result["id"])

    def test_get_user_by_email_not_found(self):
        with self.assertRaises(AssertionError):
            self.core_client.get_user_by_email(email="non_existent@email.co.uk")

    def test_get_user_by_anon_project_specific_user_id_ok(self):
        result = self.core_client.get_user_by_anon_project_specific_user_id(
            anon_project_specific_user_id="1a03cb39-b669-44bb-a69e-98e6a521d758"
        )
        self.assertEqual("altha@email.co.uk", result["email"])

    def test_get_user_by_anon_project_specific_user_id_not_found(self):
        with self.assertRaises(AssertionError):
            self.core_client.get_user_by_anon_project_specific_user_id(
                anon_project_specific_user_id="1a03cb39-b669-44bb-a69e-98e6a521d757"
            )

    def test_get_user_task_from_anon_user_task_id_ok(self):
        result = self.core_client.get_user_task_from_anon_user_task_id(
            anon_user_task_id="3dce6e9c-9b20-4d7f-a266-9967553dbc16"
        )
        self.assertEqual(
            "273b420e-09cb-419c-8b57-b393595dba78", result["project_task_id"]
        )

    def test_patch_user_ok(self):
        result = self.core_client.patch_user(
            user_id="d1070e81-557e-40eb-a7ba-b951ddb7ebdc",
            jsonpatch=[
                {"op": "replace", "path": "/title", "value": "Sir"},
                {"op": "replace", "path": "/auth0_id", "value": "new-auth0-id"},
            ],
        )
        self.assertEqual(HTTPStatus.NO_CONTENT, result["statusCode"])

    def test_post_user_ok(self):
        # generate random email prefix to avoid database validation errors on subsequent runs
        letters = string.ascii_lowercase
        email_prefix = "".join(random.choice(letters) for i in range(10))
        result = self.core_client.post_user(
            user_dict={
                "email": f"test_post_user_{email_prefix}@email.co.uk",
                "title": "Mr",
                "first_name": "Steven",
                "last_name": "Walcorn",
                "auth0_id": "1234abcd",
                "country_code": "IT",
                "status": "new",
            }
        )
        self.assertEqual(HTTPStatus.CREATED, result["statusCode"])

    def test_create_user_task(self):
        # Create a new user so that this test won't break if run multiple
        # times (which happens if you use a hardcoded user id).
        letters = string.ascii_lowercase
        email_prefix = "".join(random.choice(letters) for i in range(10))
        result = self.core_client.post_user(
            user_dict={
                "email": f"test_post_user_{email_prefix}@email.co.uk",
                "title": "Mr",
                "first_name": "Steven",
                "last_name": "Walcorn",
                "auth0_id": "1234abcd",
                "country_code": "IT",
                "status": "new",
            }
        )

        user_task_data = {
            "user_id": json.loads(result.get("body")).get("id"),
            "project_task_id": "f60d5204-57c1-437f-a085-1943ad9d174f",
            "consented": "2018-07-19 16:16:56.087895+01",
            "display_method": "iframe",
        }
        result = self.core_client.create_user_task(user_task_data)
        self.assertEqual(HTTPStatus.CREATED, result["statusCode"])

    def test_list_user_lists(self):
        results = self.core_client.list_user_lists()
        assert len(results) > 0

    def test_create_user_email_despatch(self):
        result = self.core_client.create_user_email_despatch(
            user_email_despatch_data={
                "user_id": "d1070e81-557e-40eb-a7ba-b951ddb7ebdc",
                "user_task_id": "615ff0e6-0b41-4870-b9db-527345d1d9e5",
                "group_email_despatch_id": None,
                "template_id": "participant_consent",
            }
        )

        assert result["statusCode"] == HTTPStatus.CREATED


class TestCoreApiUtilitiesGroupEmailDespatch(test_utils.BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.core_client = CoreApiClient(get_environment_name())

    def setUp(self):
        self.data = {
            "project_id": "97406352-d482-428e-abd1-a3e0b6f550e4",
            "sender_id": "d1070e81-557e-40eb-a7ba-b951ddb7ebdc",
            "template_id": "unittests_email_template_3",
            "description": "Test email despatch",
        }

    def test_create_and_update_email_despatch(self):
        result = self.core_client.post_group_email_despatch(
            group_email_despatch_dict=self.data
        )

        assert result["statusCode"] == HTTPStatus.CREATED

        id = json.loads(result["body"])["id"]

        result = self.core_client.patch_group_email_despatch(
            group_email_despatch_id=id,
            jsonpatch=[
                {"op": "replace", "path": "/description", "value": "This is a test"}
            ],
        )

        assert result["statusCode"] == HTTPStatus.NO_CONTENT

    def test_update_group_email_despatch_send_start_date(self):
        result = self.core_client.post_group_email_despatch(
            group_email_despatch_dict=self.data
        )

        assert result["statusCode"] == HTTPStatus.CREATED
        assert json.loads(result["body"])["send_start_date"] is None

        id = json.loads(result["body"])["id"]

        result = self.core_client.patch_user_email_despatch_send_start_date(
            group_email_despatch_id=id
        )

        assert result["statusCode"] == HTTPStatus.OK

        result = self.core_client.get_group_email_despatch(id)
        assert json.loads(result["body"])["send_start_date"] is not None

        # Test that it fails if the send_start_date is already set. Because
        # the lambda is wrapped in a decorator that checks the status code,
        # this will just throw an AssertionError, instead of returning a 400.
        # This is expected behaviour, so the tests just have to catch the exception.
        with self.assertRaises(AssertionError):
            self.core_client.patch_user_email_despatch_send_start_date(
                group_email_despatch_id=id
            )

    def test_update_group_email_despatch_send_end_date(self):
        result = self.core_client.post_group_email_despatch(
            group_email_despatch_dict=self.data
        )

        assert result["statusCode"] == HTTPStatus.CREATED
        assert json.loads(result["body"])["send_end_date"] is None

        id = json.loads(result["body"])["id"]

        result = self.core_client.patch_user_email_despatch_send_end_date(
            group_email_despatch_id=id
        )

        assert result["statusCode"] == HTTPStatus.OK

        result = self.core_client.get_group_email_despatch(id)
        assert json.loads(result["body"])["send_end_date"] is not None

        # Test that it fails if the send_end_date is already set. Because
        # the lambda is wrapped in a decorator that checks the status code,
        # this will just throw an AssertionError, instead of returning a 400.
        # This is expected behaviour, so the tests just have to catch the exception.
        with self.assertRaises(AssertionError):
            self.core_client.patch_user_email_despatch_send_end_date(
                group_email_despatch_id=id
            )

    def test_delete_group_email_despatch(self):
        result = self.core_client.post_group_email_despatch(
            group_email_despatch_dict=self.data
        )

        assert result["statusCode"] == HTTPStatus.CREATED

        id = json.loads(result["body"])["id"]

        result = self.core_client.delete_group_email_despatch(
            group_email_despatch_id=id
        )

        assert result["statusCode"] == HTTPStatus.NO_CONTENT

    def test_list_group_email_despatch_users_ok(self):
        user_ids = self.core_client.list_group_email_despatch_users(
            "24ae97ba-f79a-4088-9609-b6aac53f2138"
        )
        self.assertEqual(
            [
                "d1070e81-557e-40eb-a7ba-b951ddb7ebdc",
                "e067ed7b-bc98-454f-9c5e-573e2da5705c",
            ],
            user_ids,
        )

    def test_get_group_email_despatch_ok(self):
        ged = self.core_client.get_group_email_despatch(
            "eb368275-08d3-4e7a-9b75-b66c79e551cb"
        )

        assert ged["statusCode"] == HTTPStatus.OK
        self.assertDictEqual(
            {
                "id": "eb368275-08d3-4e7a-9b75-b66c79e551cb",
                "created": "2023-05-18T08:28:09.666194+00:00",
                "modified": "2023-05-18T08:28:28.846819+00:00",
                "send_start_date": "2023-05-18T08:27:48+00:00",
                "send_end_date": "2023-05-18T08:27:50+00:00",
                "scheduled_date": "2023-05-18T08:27:52+00:00",
                "template_id": "unittests_email_template_1",
                "template_params": None,
                "description": "previous_email",
                "project_id": "ce36d4d9-d3d3-493f-98e4-04f4b29ccf49",
                "sender_id": "8518c7ed-1df4-45e9-8dc4-d49b57ae0663",
            },
            json.loads(ged["body"]),
        )

    def test_get_group_email_despatch_not_ok(self):
        ged = self.core_client.get_group_email_despatch(
            "eb368275-08d3-4e7a-9b75-b66c79e551cc"
        )

        assert ged["statusCode"] == HTTPStatus.NOT_FOUND
