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


DEFAULT_TEST_TABLE_NAME = 'UnitTestData'
SORTKEY_TEST_TABLE_NAME = 'UnitTestDataSortKey'
TEST_TABLE_STACK = 'thiscovery-events'
TIME_TOLERANCE_SECONDS = 10

TEST_ITEM_01 = {
    'key': 'test01',
    'item_type': 'test data',
    'details': {'att1': 'val1', 'att2': 'val2'},
}

TEST_ITEM_02 = {
    **TEST_ITEM_01,
    'processing_status': 'new',
    'country_code': 'GB',
}

TEST_ITEM_03 = {
    **TEST_ITEM_01,
    'bool_attribute': True,
}

TEST_ITEM_SORT_KEY_01 = {
    'key': 'test_data_with_sort_key',
    'item_type': 'test data',
    'details': {'att1': 'val1', 'att2': 'val2'},
    'data_sort': 'test_sort_01',
}

TEST_ITEM_SORT_KEY_02 = {
    **TEST_ITEM_SORT_KEY_01,
    'processing_status': 'new',
    'country_code': 'GB',
}


class TestDynamoDbBase(test_utils.BaseTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ddb = ddb_utils.Dynamodb(stack_name=TEST_TABLE_STACK)


class TestDynamoDbSortKeys(TestDynamoDbBase):

    def setUp(self):
        self.ddb.delete_all(
            table_name=SORTKEY_TEST_TABLE_NAME,
            key_name='data_type',
            sort_key_name='data_sort',
        )

    def put_test_items_with_sort_key(self, integer):
        """
        Puts "integer" test items in SORTKEY_TEST_TABLE_NAME
        :param integer: desired number of test items
        """
        for n in range(integer):
            self.ddb.put_item(
                table_name=SORTKEY_TEST_TABLE_NAME,
                key='test_data_with_sort_key',
                item_type='test data',
                item_details={'att1': f'val1.{n}', 'att2': f'val2.{n}'},
                item={},
                update_allowed=True,
                key_name='data_type',
                sort_key={'data_sort': f'test{n:03}'},
            )

    def common_assertions_sort_key(self, item, result, relevant_datetime_name):
        self.assertEqual(item['key'], result['data_type'])
        self.assertEqual(item['item_type'], result['type'])
        self.assertEqual(item['details'], result['details'])
        self.assertEqual(item['data_sort'], result['data_sort'])
        self.now_datetime_test_and_remove(result, relevant_datetime_name, tolerance=TIME_TOLERANCE_SECONDS)

    def test_put_and_get_with_sort_key_ok(self):
        item = TEST_ITEM_SORT_KEY_01
        self.ddb.put_item(
            table_name=SORTKEY_TEST_TABLE_NAME,
            key=item['key'],
            item_type=item['item_type'],
            item_details=item['details'],
            item=item,
            update_allowed=False,
            key_name='data_type',
            sort_key={
                'data_sort': item['data_sort']
            },
        )
        result = self.ddb.get_item(
            table_name=SORTKEY_TEST_TABLE_NAME,
            key=item['key'],
            key_name='data_type',
            sort_key={
                'data_sort': item['data_sort']
            },
        )
        self.common_assertions_sort_key(item, result, 'created')

    def test_put_update_with_sort_key_ok(self):
        item = TEST_ITEM_SORT_KEY_01
        self.ddb.put_item(
            table_name=SORTKEY_TEST_TABLE_NAME,
            key=item['key'],
            item_type=item['item_type'],
            item_details=item['details'],
            item=item,
            update_allowed=False,
            key_name='data_type',
            sort_key={
                'data_sort': item['data_sort']
            },
        )
        item['details'] = {'att1': 'val1', 'att3': 'val3'}
        self.ddb.put_item(
            table_name=SORTKEY_TEST_TABLE_NAME,
            key=item['key'],
            item_type=item['item_type'],
            item_details=item['details'],
            item=item,
            update_allowed=True,
            key_name='data_type',
            sort_key={
                'data_sort': item['data_sort']
            },
        )
        result = self.ddb.get_item(
            table_name=SORTKEY_TEST_TABLE_NAME,
            key=item['key'],
            key_name='data_type',
            sort_key={
                'data_sort': item['data_sort']
            },
        )
        self.common_assertions_sort_key(item, result, 'modified')

    def test_put_update_with_sort_key_fail(self):
        item = TEST_ITEM_SORT_KEY_01
        self.ddb.put_item(
            table_name=SORTKEY_TEST_TABLE_NAME,
            key=item['key'],
            item_type=item['item_type'],
            item_details=item['details'],
            item=item,
            update_allowed=False,
            key_name='data_type',
            sort_key={
                'data_sort': item['data_sort']
            },
        )
        with self.assertRaises(utils.DetailedValueError) as error:
            self.ddb.put_item(
                table_name=SORTKEY_TEST_TABLE_NAME,
                key=item['key'],
                item_type=item['item_type'],
                item_details=item['details'],
                item=item,
                update_allowed=False,
                key_name='data_type',
                sort_key={
                    'data_sort': item['data_sort']
                },
            )
        self.assertEqual('ConditionalCheckFailedException', error.exception.details['error_code'])

    def test_update_with_sort_key_ok(self):
        item = TEST_ITEM_SORT_KEY_02
        self.ddb.put_item(
            table_name=SORTKEY_TEST_TABLE_NAME,
            key=item['key'],
            item_type=item['item_type'],
            item_details=item['details'],
            item=item,
            update_allowed=False,
            key_name='data_type',
            sort_key={
                'data_sort': item['data_sort']
            },
        )
        item['details'] = {'att1': 'val1', 'att3': 'val3'}
        self.ddb.update_item(
            table_name=SORTKEY_TEST_TABLE_NAME,
            key=item['key'],
            name_value_pairs={'details': item['details']},
            key_name='data_type',
            sort_key={
                'data_sort': item['data_sort']
            },
        )
        result = self.ddb.get_item(
            table_name=SORTKEY_TEST_TABLE_NAME,
            key=item['key'],
            key_name='data_type',
            sort_key={
                'data_sort': item['data_sort']
            },
        )
        self.common_assertions_sort_key(item, result, 'modified')
        self.assertEqual(item['country_code'], result['country_code'])


class TestDynamoDB(TestDynamoDbBase):

    def setUp(self):
        self.ddb.delete_all(DEFAULT_TEST_TABLE_NAME)

    def put_test_items(self, integer):
        """
        Puts "integer" test items in DEFAULT_TEST_TABLE_NAME
        :param integer: desired number of test items
        """
        for n in range(integer):
            self.ddb.put_item(
                table_name=DEFAULT_TEST_TABLE_NAME,
                key=f'test{n:03}',
                item_type='test data',
                item_details={'att1': f'val1.{n}', 'att2': f'val2.{n}'},
                item={},
                update_allowed=True
            )

    def common_assertions(self, item, result, relevant_datetime_name):
        self.assertEqual(item['key'], result['id'])
        self.assertEqual(item['item_type'], result['type'])
        self.assertEqual(item['details'], result['details'])
        self.now_datetime_test_and_remove(result, relevant_datetime_name, tolerance=TIME_TOLERANCE_SECONDS)

    def test_get_table_ok(self):
        table = self.ddb.get_table(DEFAULT_TEST_TABLE_NAME)
        items = self.ddb.scan(DEFAULT_TEST_TABLE_NAME)
        self.assertEqual('ACTIVE', table.table_status)
        self.assertEqual(0, len(items))

    def test_put_and_get_ok(self):
        item = TEST_ITEM_01
        self.ddb.put_item(DEFAULT_TEST_TABLE_NAME, item['key'], item['item_type'], item['details'], item, False)
        result = self.ddb.get_item(DEFAULT_TEST_TABLE_NAME, item['key'])
        self.common_assertions(item, result, 'created')

    def test_put_and_get_ok_with_bool_attribute(self):
        item = TEST_ITEM_03
        self.ddb.put_item(DEFAULT_TEST_TABLE_NAME, item['key'], item['item_type'], item['details'], item, False)
        result = self.ddb.get_item(DEFAULT_TEST_TABLE_NAME, item['key'])
        self.common_assertions(item, result, 'created')

    def test_put_update_ok(self):
        item = TEST_ITEM_01
        self.ddb.put_item(DEFAULT_TEST_TABLE_NAME, item['key'], item['item_type'], item['details'], item, False)
        item['details'] = {'att1': 'val1', 'att3': 'val3'}
        self.ddb.put_item(DEFAULT_TEST_TABLE_NAME, item['key'], item['item_type'], item['details'], item, update_allowed=True)
        result = self.ddb.get_item(DEFAULT_TEST_TABLE_NAME, item['key'])
        self.common_assertions(item, result, 'modified')

    def test_put_update_fail(self):
        item = TEST_ITEM_01
        self.ddb.put_item(DEFAULT_TEST_TABLE_NAME, item['key'], item['item_type'], item['details'], item, False)
        with self.assertRaises(utils.DetailedValueError) as error:
            self.ddb.put_item(DEFAULT_TEST_TABLE_NAME, item['key'], item['item_type'], item['details'], item, False)
        self.assertEqual('ConditionalCheckFailedException', error.exception.details['error_code'])

    def test_scan(self):
        self.put_test_items(3)
        items = self.ddb.scan(DEFAULT_TEST_TABLE_NAME)
        self.assertEqual(3, len(items))
        self.assertEqual('test002', items[2]['id'])

    def test_scan_filter_list(self):
        self.put_test_items(4)
        items = self.ddb.scan(DEFAULT_TEST_TABLE_NAME, 'id', ['test002'])

        self.assertEqual(1, len(items))
        self.assertEqual({'att1': 'val1.2', 'att2': 'val2.2'}, items[0]['details'])

    def test_scan_filter_bool(self):
        self.put_test_items(4)
        item = TEST_ITEM_03
        self.ddb.put_item(DEFAULT_TEST_TABLE_NAME, item['key'], item['item_type'], item['details'], item, True)
        items = self.ddb.scan(table_name=DEFAULT_TEST_TABLE_NAME, filter_attr_name='bool_attribute',
                              filter_attr_values=True)
        self.assertEqual(1, len(items))
        self.assertEqual({'att2': 'val2', 'att1': 'val1'}, items[0]['details'])

    def test_scan_filter_string(self):
        self.put_test_items(4)
        items = self.ddb.scan(DEFAULT_TEST_TABLE_NAME, 'id', 'test002')

        self.assertEqual(1, len(items))
        self.assertEqual({'att1': 'val1.2', 'att2': 'val2.2'}, items[0]['details'])

    def test_delete_ok(self):
        self.put_test_items(1)
        key = 'test000'
        self.ddb.delete_item(DEFAULT_TEST_TABLE_NAME, key)
        result = self.ddb.get_item(DEFAULT_TEST_TABLE_NAME, key)
        self.assertIsNone(result)

    def test_update_ok(self):
        item = TEST_ITEM_02
        self.ddb.put_item(DEFAULT_TEST_TABLE_NAME, item['key'], item['item_type'], item['details'], item, False)
        item['details'] = {'att1': 'val1', 'att3': 'val3'}
        self.ddb.update_item(DEFAULT_TEST_TABLE_NAME, item['key'], {'details': item['details']})
        result = self.ddb.get_item(DEFAULT_TEST_TABLE_NAME, item['key'])
        self.common_assertions(item, result, 'modified')
        self.assertEqual(item['country_code'], result['country_code'])
