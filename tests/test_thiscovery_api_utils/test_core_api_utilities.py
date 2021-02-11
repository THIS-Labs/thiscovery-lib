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
from http import HTTPStatus
from pprint import pprint
import thiscovery_dev_tools.testing_tools as test_utils
from thiscovery_lib.core_api_utilities import CoreApiClient


class TestCoreApiUtilities(test_utils.BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.core_client = CoreApiClient(
            env_override=local.dev_config.UNIT_TEST_NAMESPACE[1:-1],
        )

    def test_get_user_by_email_ok(self):
        result = self.core_client.get_user_by_email(
            email='delia@email.co.uk'
        )
        self.assertEqual('35224bd5-f8a8-41f6-8502-f96e12d6ddde', result['id'])

    def test_get_user_by_email_not_found(self):
        with self.assertRaises(AssertionError):
            self.core_client.get_user_by_email(
                email='non_existent@email.co.uk'
            )

    def test_get_user_task_from_anon_user_task_id_ok(self):
        result = self.core_client.get_user_task_from_anon_user_task_id(
            anon_user_task_id='3dce6e9c-9b20-4d7f-a266-9967553dbc16'
        )
        self.assertEqual('273b420e-09cb-419c-8b57-b393595dba78', result['project_task_id'])
