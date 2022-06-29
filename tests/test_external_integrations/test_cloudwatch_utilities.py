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
import time
import thiscovery_dev_tools.testing_tools as test_utils
from pprint import pprint

import thiscovery_lib.utilities as utils
from thiscovery_lib.cloudwatch_utilities import CloudWatchLogsClient
from thiscovery_lib.core_api_utilities import CoreApiClient


class TestCloudWatchLogs(test_utils.BaseTestCase):
    expected_log_string = "Response from THIS Institute citizen science"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cwl_client = CloudWatchLogsClient()
        cls.logger = utils.get_logger()
        core_api_client = CoreApiClient()
        core_api_client.ping()

    def common_query_results_assertions(self, results):
        self.assertEqual(1, len(results))
        message = None
        for fields_dict in results[0]:
            if fields_dict["field"] == "@message":
                message = fields_dict["value"]
                break
        self.assertIn(self.expected_log_string, message)

    def test_describe_log_streams_ok(self):
        result = self.cwl_client.describe_log_streams(
            log_group_name="ping", stack_name="thiscovery-core"
        )
        self.logger.debug("Latest log stream", extra={"result": result})
        self.assertIsInstance(result, list)
        expected_keys = [
            "logStreamName",
            "creationTime",
            "firstEventTimestamp",
            "lastEventTimestamp",
            "lastIngestionTime",
            "uploadSequenceToken",
            "arn",
            "storedBytes",
        ]
        self.assertCountEqual(expected_keys, result[0].keys())

    def test_get_latest_log_event_ok(self):
        attempts = 0
        while attempts < 10:
            result = self.cwl_client.get_latest_log_events(
                log_group_name="ping", stack_name="thiscovery-core"
            )
            if result["events"]:
                break
            time.sleep(1)
            attempts += 1
        expected_event_found = False
        for event in result["events"]:
            if self.expected_log_string in event["message"]:
                expected_event_found = True
        self.assertTrue(expected_event_found)

    def test_find_in_log_message_ok(self):
        result = self.cwl_client.find_in_log_message(
            log_group_name="ping",
            query_string=self.expected_log_string,
            stack_name="thiscovery-core",
        )
        self.assertIsInstance(result, str)

    def test_find_in_log_message_query_list_ok(self):
        result = self.cwl_client.find_in_log_message(
            log_group_name="ping",
            query_string=[self.expected_log_string, "Function result"],
            stack_name="thiscovery-core",
        )
        self.assertIsInstance(result, str)

    def test_find_in_log_message_query_list_not_found_ok(self):
        result = self.cwl_client.find_in_log_message(
            log_group_name="ping",
            query_string=[self.expected_log_string, "this is not in the logs"],
            stack_name="thiscovery-core",
            timeout=1,
        )
        self.assertIsNone(result)

    def test_find_in_log_message_query_list_OR_ok(self):
        result = self.cwl_client.find_in_log_message(
            log_group_name="ping",
            query_string=[self.expected_log_string, "this is not in the logs"],
            stack_name="thiscovery-core",
            timeout=1,
            conditional_operator="OR",
        )
        self.assertIsInstance(result, str)

    def test_find_in_log_message_not_found_ok(self):
        result = self.cwl_client.find_in_log_message(
            log_group_name="ping",
            query_string="this string is not present in logs",
            stack_name="thiscovery-core",
            timeout=1,
        )
        self.assertIsNone(result)

    def test_find_in_log_message_too_old(self):
        result = self.cwl_client.find_in_log_message(
            log_group_name="ping",
            query_string=self.expected_log_string,
            stack_name="thiscovery-core",
            earliest_log=3000000000000,
            timeout=1,
        )
        self.assertIsNone(result)

    def test_find_in_log_message_invalid_query_string_type(self):
        with self.assertRaises(utils.DetailedValueError):
            self.cwl_client.find_in_log_message(
                log_group_name="ping",
                query_string={"string_to_query": self.expected_log_string},
                stack_name="thiscovery-core",
                timeout=1,
            )

    def test_find_in_log_message_invalid_conditional_operator(self):
        with self.assertRaises(utils.DetailedValueError):
            self.cwl_client.find_in_log_message(
                log_group_name="ping",
                query_string=[self.expected_log_string, "this is not in the logs"],
                stack_name="thiscovery-core",
                timeout=1,
                conditional_operator="ALL",
            )

    def test_query_one_log_group_using_query_parameter(self):
        test_query = (
            f"fields @timestamp, @message"
            f" | filter @message like /{self.expected_log_string}/"
            f" | sort @timestamp desc"
            f" | limit 1"
        )
        results = self.cwl_client.query_one_log_group(
            log_group_name="ping",
            query=test_query,
            stack_name="thiscovery-core",
        )
        self.common_query_results_assertions(results)

    def test_query_one_log_group_using_query_string_parameter(self):
        results = self.cwl_client.query_one_log_group(
            log_group_name="ping",
            query_string=self.expected_log_string,
            stack_name="thiscovery-core",
            limit=1,
        )
        self.common_query_results_assertions(results)

    def test_query_one_log_group_using_list_of_query_strings(self):
        results = self.cwl_client.query_one_log_group(
            log_group_name="ping",
            query_string=["Response", "citizen", "API"],
            stack_name="thiscovery-core",
            limit=1,
        )
        self.common_query_results_assertions(results)

    def test_query_one_log_group_query_string_not_found(self):
        results = self.cwl_client.query_one_log_group(
            log_group_name="ping",
            query_string="This should not appear in the logs",
            stack_name="thiscovery-core",
            limit=1,
        )
        self.assertEqual(list(), results)

    def test_query_one_log_group_raises_error_nothing_to_query(self):
        with self.assertRaises(utils.DetailedValueError):
            self.cwl_client.query_one_log_group(
                log_group_name="ping",
                stack_name="thiscovery-core",
                limit=1,
            )
