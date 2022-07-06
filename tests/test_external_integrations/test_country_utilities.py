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
import os
import thiscovery_dev_tools.testing_tools as test_tools
import thiscovery_lib.utilities as utils
from thiscovery_lib.utilities import set_running_unit_tests, DetailedValueError
from thiscovery_lib.countries_utilities import get_country_name


class TestCountry(test_tools.BaseTestCase):
    def test_get_country_name_ok(self):
        self.assertEqual("France", get_country_name("FR"))
        self.assertEqual("United Kingdom", get_country_name("GB"))

    def test_get_country_name_fail(self):
        self.assertRaises(DetailedValueError, get_country_name, "ZX")
        self.assertRaises(DetailedValueError, get_country_name, "")
        self.assertRaises(DetailedValueError, get_country_name, "abcdef")
