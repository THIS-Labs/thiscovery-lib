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
from __future__ import annotations

import json
from abc import ABCMeta, abstractmethod
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from http import HTTPStatus

import thiscovery_lib.utilities as utils


class Dynamodb(utils.BaseClient):
    def __init__(
        self,
        stack_name="thiscovery-core",
        correlation_id=None,
        profile_name=None,
        **kwargs,
    ):
        super().__init__(
            "dynamodb",
            client_type="resource",
            correlation_id=correlation_id,
            profile_name=profile_name,
            **kwargs,
        )
        super().get_namespace()
        self.stack_name = stack_name

    def get_table(self, table_name):
        table_full_name = "-".join([self.stack_name, self.aws_namespace, table_name])
        self.logger.debug("Table full name", extra={"table_full_name": table_full_name})
        return self.client.Table(table_full_name)

    def batch_put_items(self, table_name, items, partition_key_name, item_type=None):
        """
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.batch_writer
        """
        try:
            table = self.get_table(table_name)
            with table.batch_writer() as batch:
                for item in items:
                    now = str(utils.now_with_tz())
                    item["created"] = now
                    item["modified"] = now
                    item["type"] = item.get("type", item_type)
                    batch.put_item(Item=item)
        except ClientError as ex:
            error_code = ex.response["Error"]["Code"]
            errorjson = {
                "error_code": error_code,
                "table_name": table_name,
                "item_type": item_type,
                "correlation_id": self.correlation_id,
            }
            raise utils.DetailedValueError("Dynamodb raised an error", errorjson)

    def put_item(
        self,
        table_name,
        key,
        item_type,
        item_details,
        item=dict(),
        update_allowed=False,
        correlation_id=None,
        key_name="id",
        sort_key=None,
    ):
        """
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.put_item
        Args:
            table_name (str):
            key (str):
            item_type (str):
            item_details:
            item:
            key_name:
            sort_key (dict): if the table uses a sort_key, provide a dictionary specifying it (e.g. {'added_date': '2020-11-12'})
            update_allowed:
            correlation_id:

        Returns:
        """
        try:
            table = self.get_table(table_name)

            item[key_name] = str(key)
            item["type"] = item_type
            item["details"] = item_details
            now = str(utils.now_with_tz())
            item["created"] = now
            item["modified"] = now
            if sort_key:
                item.update(sort_key)

            self.logger.info(
                "dynamodb put",
                extra={
                    "table_name": table_name,
                    "item": item,
                    "correlation_id": self.correlation_id,
                },
            )
            if update_allowed:
                result = table.put_item(Item=item)
            else:
                condition_expression = f"attribute_not_exists({key_name})"  # no need to worry about sort_key here: https://stackoverflow.com/a/32833726
                result = table.put_item(
                    Item=item, ConditionExpression=condition_expression
                )
            assert (
                result["ResponseMetadata"]["HTTPStatusCode"] == HTTPStatus.OK
            ), f"Dynamodb call failed with response {result}"
            return result
        except ClientError as ex:
            error_code = ex.response["Error"]["Code"]
            errorjson = {
                "error_code": error_code,
                "table_name": table_name,
                "item_type": item_type,
                key_name: str(key),
                "correlation_id": self.correlation_id,
            }
            raise utils.DetailedValueError("Dynamodb raised an error", errorjson)

    def update_item(
        self,
        table_name: str,
        key: str,
        name_value_pairs: dict,
        correlation_id=None,
        key_name="id",
        sort_key=None,
        **kwargs,
    ):
        """
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.update_item

        Args:
            table_name:
            key:
            name_value_pairs:
            key_name:
            sort_key (dict): if the table uses a sort_key, provide a dictionary specifying it (e.g. {'added_date': '2020-11-12'})
            correlation_id:
            **kwargs: use ReturnValues to get the item attributes as they appear before or after the update

        Returns:
            Only response metadata such as status code, unless the parameter ReturnValues is specified in **kwargs

        Notes:
            US 2951 proposes adding support for partial map updates to this function.
        """
        if correlation_id is None:
            correlation_id = utils.new_correlation_id()

        table = self.get_table(table_name)
        key_json = {key_name: key}
        if sort_key:
            key_json.update(sort_key)
        update_expr = "SET #modified = :m "
        values_expr = {":m": name_value_pairs.pop("modified", str(utils.now_with_tz()))}
        attr_names_expr = {
            "#modified": "modified"
        }  # not strictly necessary, but allows easy addition of names later
        param_count = 1
        for name, value in name_value_pairs.items():
            param_name = ":p" + str(param_count)
            if (
                name == "status"
            ):  # todo generalise this to other reserved words, and ensure it only catches whole words
                attr_name = "#a" + str(param_count)
                attr_names_expr[attr_name] = "status"
            else:
                attr_name = name
            update_expr += ", " + attr_name + " = " + param_name

            values_expr[param_name] = value

            param_count += 1

        self.logger.info(
            "dynamodb update",
            extra={
                "table_name": table_name,
                "key": json.dumps(key_json),
                "update_expr": update_expr,
                "values_expr": values_expr,
                "correlation_id": correlation_id,
            },
        )
        return table.update_item(
            Key=key_json,
            UpdateExpression=update_expr,
            ExpressionAttributeValues=values_expr,
            ExpressionAttributeNames=attr_names_expr,
            **kwargs,
        )

    def scan(
        self,
        table_name: str,
        filter_attr_name: str = None,
        filter_attr_values=None,
        table_name_verbatim=False,
    ):
        """
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.scan

        Return:
            A list of dictionaries, each representing an item in the Dynamodb table
        """
        if table_name_verbatim:
            table = self.client.Table(table_name)
        else:
            table = self.get_table(table_name)

        # accept string but make it into a list for later processing
        if isinstance(filter_attr_values, str) or isinstance(filter_attr_values, bool):
            filter_attr_values = [filter_attr_values]
        self.logger.info(
            "dynamodb scan",
            extra={
                "table_name": table_name,
                "filter_attr_name": filter_attr_name,
                "filter_attr_value": str(filter_attr_values),
                "correlation_id": self.correlation_id,
            },
        )
        if filter_attr_name is None:
            response = table.scan()
        else:
            filter_expr = Attr(filter_attr_name).eq(filter_attr_values[0])
            for value in filter_attr_values[1:]:
                filter_expr = filter_expr | Attr(filter_attr_name).eq(value)
            response = table.scan(FilterExpression=filter_expr)
        items = response["Items"]
        self.logger.info(
            "dynamodb scan result",
            extra={"count": str(len(items)), "correlation_id": self.correlation_id},
        )
        return items

    def query(
        self,
        table_name,
        table_name_verbatim=False,
        filter_attr_name=None,
        filter_attr_values=None,
        **kwargs,
    ):
        """
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Table.query
        """
        if table_name_verbatim:
            table = self.client.Table(table_name)
        else:
            table = self.get_table(table_name)
        if isinstance(filter_attr_values, str) or isinstance(filter_attr_values, bool):
            filter_attr_values = [filter_attr_values]

        if filter_attr_name is None:
            response = table.query(**kwargs)
        else:
            filter_expr = Attr(filter_attr_name).eq(filter_attr_values[0])
            for value in filter_attr_values[1:]:
                filter_expr = filter_expr | Attr(filter_attr_name).eq(value)
            response = table.query(FilterExpression=filter_expr, **kwargs)
        return response.get("Items")

    def get_item(
        self,
        table_name: str,
        key: str,
        correlation_id=None,
        key_name="id",
        sort_key=None,
    ):
        """
        Args:
            table_name:
            key:
            key_name:
            sort_key (dict): if the table uses a sort_key, provide a dictionary specifying it (e.g. {'added_date': '2020-11-12'})
            correlation_id:

        Returns:

        """
        if correlation_id is None:
            correlation_id = utils.new_correlation_id()
        table = self.get_table(table_name)
        key_json = {key_name: key}
        if sort_key:
            key_json.update(sort_key)
        self.logger.info(
            "dynamodb get",
            extra={
                "table_name": table_name,
                "key": json.dumps(key_json),
                "correlation_id": correlation_id,
            },
        )
        response = table.get_item(Key=key_json)
        if "Item" in response:
            return response["Item"]
        else:
            # not found
            return None

    def delete_item(
        self,
        table_name: str,
        key: str,
        correlation_id=None,
        key_name="id",
        sort_key=None,
    ):
        if correlation_id is None:
            correlation_id = utils.new_correlation_id()
        table = self.get_table(table_name)
        key_json = {key_name: key}
        if sort_key:
            key_json.update(sort_key)
        self.logger.info(
            "dynamodb delete",
            extra={
                "table_name": table_name,
                "key": json.dumps(key_json),
                "correlation_id": correlation_id,
            },
        )
        return table.delete_item(Key=key_json)

    def batch_delete_items(self, table_name, keys):
        """
        Args:
            table_name:
            keys (list): Ids of items to delete
        Returns:
            None (ddb batch_writer does not return anything; see this thread for details:
            https://stackoverflow.com/a/55424350)
        """
        table = self.get_table(table_name=table_name)
        with table.batch_writer() as batch:
            for item_id in keys:
                batch.delete_item(Key={"id": item_id})

    def delete_all(
        self,
        table_name: str,
        table_name_verbatim=False,
        correlation_id=None,
        key_name="id",
        sort_key_name=None,
    ):
        if correlation_id is None:
            correlation_id = utils.new_correlation_id()
        if table_name_verbatim:
            table = self.client.Table(table_name)
        else:
            table = self.get_table(table_name)
        items = self.scan(table_name, table_name_verbatim=table_name_verbatim)
        for item in items:
            key = item[key_name]
            key_json = {key_name: key}
            if sort_key_name:
                sort_key = item[sort_key_name]
                key_json.update({sort_key_name: sort_key})
            self.logger.info(
                "dynamodb delete_all",
                extra={
                    "table_name": table_name,
                    "key": key_json,
                    "correlation_id": correlation_id,
                },
            )
            table.delete_item(Key=key_json)

    def wait_until_table_exists(
        self,
        table_name: str,
        table_name_verbatim=False,
    ):
        if table_name_verbatim:
            table = self.client.Table(table_name)
        else:
            table = self.get_table(table_name)
        return table.wait_until_exists()


class DdbBaseTable(metaclass=ABCMeta):
    """
    Base abstract class representing a Ddb table
    """

    name = None
    partition = None
    sort = None

    def __init__(self, stack_name, correlation_id=None, profile_name=None, **kwargs):
        assert self.name, f"{self.__class__}.name must be set"
        assert self.partition, f"{self.__class__}.partition must be set"
        self.correlation_id = correlation_id
        self._ddb_client = Dynamodb(
            stack_name=stack_name,
            correlation_id=correlation_id,
            profile_name=profile_name,
            **kwargs,
        )
        self.table = None

    def get_table(self):
        if self.table is None:
            self.table = self._ddb_client.get_table(self.name)

    def query(self, **kwargs):
        """
        Performs query using the existing table resource object, which should
        be quicker than calling _ddb_client.query (that method always has to
        create a new table resource object first)

        Args:
            **kwargs:

        Returns:
            List of matching items
        """

        self.get_table()
        r = self.table.query(**kwargs)
        assert (
            r["ResponseMetadata"]["HTTPStatusCode"] == HTTPStatus.OK
        ), f"Dynamodb query failed with response: {r}"
        return r.get("Items", list())

    def query_index_by_partition_only(
        self, index_name, index_partition_name, index_partition_value
    ):
        return self.query(
            IndexName=index_name,
            KeyConditionExpression=f"{index_partition_name} = :{index_partition_name}",
            ExpressionAttributeValues={
                f":{index_partition_name}": index_partition_value
            },
        )

    def delete_all(self):
        return self._ddb_client.delete_all(
            table_name=self.name,
            table_name_verbatim=False,
            correlation_id=self.correlation_id,
            key_name=self.partition,
            sort_key_name=self.sort,
        )

    def scan(self, **kwargs):
        return self._ddb_client.scan(
            table_name=self.name,
            filter_attr_name=kwargs.get("filter_attr_name"),
            filter_attr_values=kwargs.get("filter_attr_values"),
            table_name_verbatim=kwargs.get("table_name_verbatim", False),
        )

    def resolve_keys(self, **kwargs):
        key = kwargs.pop(self.partition)
        sort_key = kwargs.pop(self.sort, None)
        if sort_key:
            sort_key = {self.sort: sort_key}
        return key, sort_key, kwargs

    def get_item(self, **kwargs):
        """
        Args:
            **kwargs: DdbBaseItem.as_dict()

        Returns:

        """
        key, sort_key, kwargs = self.resolve_keys(**kwargs)
        return self._ddb_client.get_item(
            table_name=self.name,
            key=key,
            key_name=self.partition,
            sort_key=sort_key,
        )

    def put_item(self, **kwargs):
        """
        Args:
            **kwargs: DdbBaseItem.as_dict()

        Returns:

        """
        key, sort_key, kwargs = self.resolve_keys(**kwargs)
        update = kwargs.pop("update", False)
        return self._ddb_client.put_item(
            table_name=self.name,
            key=key,
            key_name=self.partition,
            item_type=kwargs.pop("item_type", "ddb_item"),
            item_details=kwargs.pop("item_details", None),
            item=kwargs,
            sort_key=sort_key,
            update_allowed=update,
        )

    def update_item(self, **kwargs):
        sort_key = None
        if self.sort:
            sort_key = {self.sort: kwargs["sort"]}
        return self._ddb_client.update_item(
            table_name=self.name,
            key=kwargs["partition"],
            key_name=self.partition,
            name_value_pairs=kwargs["name_value_pairs"],
            sort_key=sort_key,
        )


class DdbBaseItem(metaclass=ABCMeta):
    """
    Base abstract class representing a Ddb item
    """

    def __init__(self, table: DdbBaseTable, ddb_client=None):
        """
        Args:
            table: table class for this item type
        """
        self._table = table
        self._ddb_client = ddb_client

    def __repr__(self):
        return self.as_dict()

    def as_dict(self):
        return {
            k: v
            for k, v in self.__dict__.items()
            if (k[0] != "_") and (k not in ["created", "modified"])
        }

    def from_dict(self, item_dict):
        self.__dict__.update(item_dict)

    def get(self):
        result = self._table.get_item(**self.as_dict())
        if result:
            self.from_dict(result)
        return result

    def put(self, update=False):
        kwargs = {
            **self.as_dict(),
            "update": update,
        }
        return self._table.put_item(**kwargs)
