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
import thiscovery_dev_tools.testing_tools as test_utils
from thiscovery_lib.sns_utilities import SnsClient
from pprint import pprint


class TestSns(test_utils.BaseTestCase):

    def test_dict_to_plaintext_list(self):
        test_dict = {
            'anon_project_specific_user_id': 'f2fac677-cb2c-42a0-9fa6-494059352569',
            'anon_user_task_id': None,
            'appointment_type_id': 123456,
            'appointment_datetime': '2021-01-08T10:15:00+0000',
            'calendar_name': 'Andre',
            'calendar_id': 123456,
            'appointment_type': 'Interview for GPs',
            'appointment_id': 123456,
        }
        expected_result = '    - anon_project_specific_user_id: f2fac677-cb2c-42a0-9fa6-494059352569\n' \
                          '    - anon_user_task_id: None\n' \
                          '    - appointment_type_id: 123456\n' \
                          '    - appointment_datetime: 2021-01-08T10:15:00+0000\n' \
                          '    - calendar_name: Andre\n' \
                          '    - calendar_id: 123456\n' \
                          '    - appointment_type: Interview for GPs\n' \
                          '    - appointment_id: 123456\n'
        result = SnsClient.dict_to_plaintext_list(test_dict)
        self.assertEqual(expected_result, result)
