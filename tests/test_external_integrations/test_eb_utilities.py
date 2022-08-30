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

import thiscovery_lib.utilities as utils
from thiscovery_lib import dynamodb_utilities as ddb_utils
from thiscovery_lib.eb_utilities import ThiscoveryEvent

from pprint import pprint


class TestThiscoveryEvent(test_utils.BaseTestCase):
    min_event = {
        "detail-type": "test_event",
        "detail": {"description": "this is a test event"},
    }

    def test_minimum_init_ok(self):
        te = ThiscoveryEvent(event=self.min_event)
        expected_keys = [
            "detail",
            "detail_type",
            "event_source",
            "event_time",
        ]
        self.assertCountEqual(expected_keys, list(te.__dict__.keys()))
        self.assertEqual("thiscovery", te.event_source)

    def test_init_with_optional_attributes_ok(self):
        test_event = {
            **self.min_event,
            "source": "qualtrics",
            "event_time": "test_event_time",
        }
        te = ThiscoveryEvent(event=test_event)
        self.assertEqual("qualtrics", te.event_source)
        self.assertEqual("test_event_time", te.event_time)
