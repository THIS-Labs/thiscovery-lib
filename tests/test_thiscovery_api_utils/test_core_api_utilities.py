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

import random
import string
import thiscovery_dev_tools.testing_tools as test_utils

from http import HTTPStatus
from pprint import pprint
from thiscovery_lib.core_api_utilities import CoreApiClient


class TestCoreApiUtilities(test_utils.BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.core_client = CoreApiClient(
            env_override=local.dev_config.UNIT_TEST_NAMESPACE[1:-1],
        )

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
        self.assertEqual(expected_user, result)

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
