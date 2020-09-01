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
import unittest

import thiscovery_lib.qualtrics as qualtrics
from thiscovery_lib.utilities import set_running_unit_tests
from tests.test_data import QUALTRICS_TEST_OBJECTS


class TestResponsesClient(unittest.TestCase):
    test_survey_id = QUALTRICS_TEST_OBJECTS['unittest-survey-1']['id']
    test_response_id = QUALTRICS_TEST_OBJECTS['unittest-survey-1']['response_1_id']

    @classmethod
    def setUpClass(cls):
        set_running_unit_tests(True)
        cls.responses_client = qualtrics.ResponsesClient(cls.test_survey_id)

    @classmethod
    def tearDownClass(cls):
        set_running_unit_tests(False)

    def test_responses_01_retrieve_response_ok(self):
        response = self.responses_client.retrieve_response(response_id=self.test_response_id)
        self.assertEqual('200 - OK', response['meta']['httpStatus'])
        expected_result = {
            'displayedFields': ['QID1',
                                'QID7_TEXT',
                                'QID3',
                                'QID2',
                                'QID5_TEXT',
                                'QID8_TEXT',
                                'QID4',
                                'QID6_TEXT'],
            'displayedValues': {'QID1': [1, 2],
                                'QID2': [1, 2],
                                'QID3': [1, 2],
                                'QID4': [1, 2]},
            'labels': {'QID1': 'yes',
                       'QID1_DO': ['yes', 'no'],
                       'QID2': 'no',
                       'QID2_DO': ['yes', 'no'],
                       'QID3': 'yes',
                       'QID3_DO': ['yes', 'no'],
                       'QID4': 'no',
                       'QID4_DO': ['yes', 'no'],
                       'finished': 'True',
                       'status': 'IP Address'},
            'responseId': 'R_1BziZVeffoDpTQl',
            'values': {'QID1': 1,
                       'QID1_DO': ['1', '2'],
                       'QID2': 2,
                       'QID2_DO': ['1', '2'],
                       'QID3': 1,
                       'QID3_DO': ['1', '2'],
                       'QID4': 2,
                       'QID4_DO': ['1', '2'],
                       'QID5_TEXT': 'Much better.',
                       'QID6_TEXT': 'Much worse.',
                       'distributionChannel': 'anonymous',
                       'duration': 25,
                       'endDate': '2020-08-24T17:42:45Z',
                       'finished': 1,
                       'progress': 100,
                       'recordedDate': '2020-08-24T17:42:46.146Z',
                       'startDate': '2020-08-24T17:42:20Z',
                       'status': 0,
                       'userLanguage': 'EN-GB'}}
        result = response['result']
        # strip PID
        del result['values']['ipAddress']
        del result['values']['locationLatitude']
        del result['values']['locationLongitude']
        self.assertCountEqual(expected_result, result)

    def test_responses_02_retrieve_schema_ok(self):
        response = self.responses_client.retrieve_survey_response_schema()
        self.assertEqual('200 - OK', response['meta']['httpStatus'])
        expected_values_properties_keys = ['QID1', 'QID10_1', 'QID10_13', 'QID10_15', 'QID10_16', 'QID10_17', 'QID10_18', 'QID10_30', 'QID10_4', 'QID10_DO', 'QID11', 'QID11_8_TEXT', 'QID11_DO', 'QID12', 'QID12_12_TEXT', 'QID12_DO', 'QID1_DO', 'QID2', 'QID2_DO', 'QID3', 'QID3_DO', 'QID4', 'QID4_DO', 'QID5_DO', 'QID5_TEXT', 'QID6_DO', 'QID6_TEXT', 'QID7_DO', 'QID7_TEXT', 'QID8_DO', 'QID8_TEXT', 'distributionChannel', 'duration', 'endDate', 'externalDataReference', 'finished', 'ipAddress', 'locationLatitude', 'locationLongitude', 'progress', 'recipientEmail', 'recipientFirstName', 'recipientLastName', 'recordedDate', 'startDate', 'status', 'userLanguage']
        self.assertCountEqual(expected_values_properties_keys, response['result']['properties']['values']['properties'].keys())


class TestDistributionsClient(unittest.TestCase):
    test_survey_id = QUALTRICS_TEST_OBJECTS['unittest-survey-1']['id']
    test_contact_list_id = QUALTRICS_TEST_OBJECTS['unittest-contact-list-1']['id']

    @classmethod
    def setUpClass(cls):
        set_running_unit_tests(True)
        cls.dist_client = qualtrics.DistributionsClient()
        # cls.created_distributions = list()

    @classmethod
    def tearDownClass(cls):
        # for dist in cls.created_distributions:
        #     cls.dist_client.delete_distribution(dist)
        set_running_unit_tests(False)

    def test_dist_01_create_retrieve_and_delete_individual_links_ok(self):
        # create
        r = self.dist_client.create_individual_links(survey_id=self.test_survey_id, contact_list_id=self.test_contact_list_id)
        self.assertEqual('200 - OK', r['meta']['httpStatus'])

        # retrieve
        distribution_id = r['result']['id']
        # self.created_distributions.append(distribution_id)
        r = self.dist_client.list_distribution_links(distribution_id, self.test_survey_id)
        self.assertEqual('200 - OK', r['meta']['httpStatus'])
        rows = r['result']['elements']
        anon_ids = [x['externalDataReference'] for x in rows]
        expected_ids = [
            '1a03cb39-b669-44bb-a69e-98e6a521d758',
            '754d3468-f6f9-46ba-8e30-e29132b925b4',
            'd4714343-305d-40b7-adc1-1b50f5575983',
            '73527dd8-6067-448a-8cd7-481a970a6a13',
            '7e6e4bca-4f0b-4f71-8660-790c1baf3b11',
            '2dc6f2c8-84d9-4705-88e9-d95731c794c9',
            'bfecaf5e-52e5-4307-baa8-7e5208ca3451',
            '922d2b14-554f-42b5-bd20-d024b5ac7214',
            '1406c523-6d12-4510-a745-271ddd9ad3e2',
            '2c8bba57-58a9-4ac7-98e8-beb34f0692c1',
            '82ca200e-66d6-455d-95bc-617f974bcb26',
            'e132c198-06d3-4200-a6c0-cc3bc7991828',
            '87b8f9a8-2400-4259-a8d9-a2f0b16d9ea1',
            'a7a8e630-cb7e-4421-a9b2-b8bad0298267',
            '3b76f205-762d-4fad-a06f-60f93bfbc5a9',
            '64cdc867-e53d-40c9-adda-f0271bcf1063',
        ]
        self.assertCountEqual(expected_ids, anon_ids)

        # delete
        r = self.dist_client.delete_distribution(distribution_id)
        self.assertEqual('200 - OK', r['meta']['httpStatus'])
