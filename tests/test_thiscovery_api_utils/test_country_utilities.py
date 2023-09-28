import local.dev_config
import local.secrets

import thiscovery_dev_tools.testing_tools as test_utils

from thiscovery_lib.countries_utilities import append_country_name_to_list

class TestCoreApiUtilities(test_utils.BaseTestCase):
    def setUp(self):
        self.user_list = [
            {
                "country_code": "GB",
                "birth_country_code": "US",
            }
        ]

    def test_append_country_name_to_list(self):
        user_list_with_country_names = append_country_name_to_list(self.user_list)
        self.assertEqual("United Kingdom", user_list_with_country_names[0]["country_name"])
        self.assertEqual("United States", user_list_with_country_names[0]["birth_country_name"])

    def test_no_error_with_missing_codes(self):
        user_list_with_country_names = append_country_name_to_list([{}])
        self.assertEqual(user_list_with_country_names[0]["country_name"], None)
        self.assertEqual(user_list_with_country_names[0]["birth_country_name"], None)
