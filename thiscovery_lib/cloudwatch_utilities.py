#
#   Thiscovery API - THIS Institute’s citizen science platform
#   Copyright (C) 2021 THIS Institute
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
"""
IMPORTANT: Please note that thiscovery-core has a cloudwatch_utilities file, which
was written before thiscovery-lib was created. Moving the methods written in
thiscovery-core to this file is the goal of US 4590
"""
import time
from typing import List, Tuple, Dict, Any, Optional, Union

import thiscovery_lib.utilities as utils


class CloudWatchLogsClient(utils.BaseClient):
    def __init__(self):
        super().__init__("logs")

    @staticmethod
    def resolve_lambda_log_group_name(
        log_group_name: str, **kwargs
    ) -> Tuple[str, Dict[str, Any]]:
        """
        If stack_name is included in kwargs this function:
            (1) interprets log_group_name as the resource name of an AWS lambda as specified in
            SAM templates (e.g. ClearBlocks). It then resolves and returns the log group name of
            that lambda function in the current runtime env (e.g. staging, test-afs25).
            (2) removes stack name from kwargs

        If stack_name is not included in kwargs, this function simply returns the input
        log_group_name and unaltered kwargs

        Args:
            log_group_name: Complete CloudWatch log group name or AWS lambda resource name
            **kwargs:
                stack_name (str): Thiscovery stack name; use only if log_group_name is an
                        AWS lambda resource name

        Returns:
            A tuple containing CloudWatch log group name and kwargs
        """
        stack_name = kwargs.pop("stack_name", None)
        if stack_name:
            return (
                f"/aws/lambda/{stack_name}-{utils.get_environment_name()}-{log_group_name}",
                kwargs,
            )
        return log_group_name, kwargs

    def describe_log_streams(
        self, log_group_name: str, order_by="LastEventTime", limit=1, **kwargs
    ) -> list:
        """
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.describe_log_streams
        Args:
            log_group_name: the name of the log group or, if stack_name is passed in kwargs, resource
                    name of lambda (as set in SAM template) whose logs we would like to query
            order_by: If the value is LogStreamName , the results are ordered by log stream name.
                    If the value is LastEventTime , the results are ordered by the event time
            limit: The maximum number of items returned
            **kwargs:
                stack_name (str): Thiscovery stack name; use only if log_group_name is an
                        AWS lambda resource name

        Returns:
            List of Cloudwatch log streams retrieved from log group
        """
        log_group_name, kwargs = self.resolve_lambda_log_group_name(
            log_group_name, **kwargs
        )
        result = self.client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy=order_by,
            limit=limit,
            descending=True,
            **kwargs,
        )
        return result["logStreams"]

    def get_log_events(
        self, log_group_name: str, log_stream_name: str, **kwargs
    ) -> Dict[str, Any]:
        """
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_log_events

        Args:
            log_group_name: the name of the log group or, if stack_name is passed in kwargs, resource
                    name of lambda (as set in SAM template) whose logs we would like to query
            log_stream_name: The name of the log stream to get events from
            **kwargs:
                stack_name (str): Thiscovery stack name; use only if log_group_name is an
                        AWS lambda resource name

        Returns:
            Dict of retrieved events (see AWS docs for details):
            {
                'events': [
                    {
                        'timestamp': 123,
                        'message': 'string',
                        'ingestionTime': 123
                    },
                ],
                'nextForwardToken': 'string',
                'nextBackwardToken': 'string'
            }
        """
        log_group_name, kwargs = self.resolve_lambda_log_group_name(
            log_group_name, **kwargs
        )
        result = self.client.get_log_events(
            logGroupName=log_group_name, logStreamName=log_stream_name, **kwargs
        )
        return result

    def get_latest_log_events(self, log_group_name: str, **kwargs) -> Dict[str, Any]:
        """
        Retrieves events from the latest log stream of log_group_name

        Args:
            log_group_name: the name of the log group or, if stack_name is passed in kwargs, resource
                    name of lambda (as set in SAM template) whose logs we would like to query
            **kwargs:
                stack_name (str): Thiscovery stack name; use only if log_group_name is an
                        AWS lambda resource name

        Returns:
            Dict of retrieved events (see AWS docs for details):
            {
                'events': [
                    {
                        'timestamp': 123,
                        'message': 'string',
                        'ingestionTime': 123
                    },
                ],
                'nextForwardToken': 'string',
                'nextBackwardToken': 'string'
            }
        """
        log_group_name, kwargs = self.resolve_lambda_log_group_name(
            log_group_name, **kwargs
        )
        log_streams = self.describe_log_streams(log_group_name=log_group_name)
        latest_stream_name = log_streams[0]["logStreamName"]
        return self.get_log_events(
            log_group_name=log_group_name, log_stream_name=latest_stream_name
        )

    def find_in_log_message(
        self,
        log_group_name: str,
        query_string: Union[str, List[str]],
        timeout=10,
        **kwargs,
    ) -> Optional[str]:
        """
        Looks up query_string in the latest logged events

        Args:
            log_group_name: the name of the log group or, if stack_name is passed in kwargs, resource
                    name of lambda (as set in SAM template) whose logs we would like to query
            query_string: String to query or list of substrings to query. If query_string is a list,
                    then conditional_operator can be passed to change query from AND (default) to OR.
            timeout: Give up after this many seconds
            **kwargs:
                stack_name (str): Thiscovery stack name; use only if log_group_name is an
                        AWS lambda resource name
                earliest_log (float): Utc timestamp; any log entries older than this value
                        will be ignored
                conditional_operator (str): AND or OR to control querying behaviour when query_string contains
                        more than one substring

        Returns:
            First found log message containing query_string if one is found;
            otherwise, returns None
        """
        log_group_name, kwargs = self.resolve_lambda_log_group_name(
            log_group_name, **kwargs
        )
        attempts = 0
        earliest_log = kwargs.get("earliest_log", 0)
        while attempts < timeout:
            latest_stream = self.get_latest_log_events(
                log_group_name=log_group_name, **kwargs
            )
            for event in latest_stream["events"]:
                if event["timestamp"] < earliest_log:
                    break
                message = event["message"]
                if isinstance(query_string, list):
                    operator = kwargs.get("conditional_operator", "AND")
                    if operator == "OR":
                        for substring in query_string:
                            if substring in message:
                                return message
                    elif operator == "AND":
                        matched_substrings = 0
                        for substring in query_string:
                            if substring in message:
                                matched_substrings += 1
                        if matched_substrings == len(query_string):
                            return message
                    else:
                        raise utils.DetailedValueError(
                            f"Unsupported conditional_operator value ({operator}). Valid values are 'AND' or 'OR'",
                            details=dict(),
                        )
                elif isinstance(query_string, str):
                    if query_string in message:
                        return message
                else:
                    raise utils.DetailedValueError(
                        f"Unsupported query_string. query_string must be a str or list, not {type(query_string)}",
                        details=dict(),
                    )
            time.sleep(1)
            attempts += 1
