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
import thiscovery_lib.utilities as utils


class CloudWatchLogsClient(utils.BaseClient):
    def __init__(self):
        super().__init__("logs")

    @staticmethod
    def resolve_lambda_name(log_group_name, **kwargs):
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
            log_group_name: the name of the log group or, if stack_name is passes in kwargs, short
                    name of lambda whose logs we would like to query
            order_by: If the value is LogStreamName , the results are ordered by log stream name.
                    If the value is LastEventTime , the results are ordered by the event time
            limit: The maximum number of items returned
            **kwargs:
                stack_name: name of stack lambda belongs to

        Returns:
        """
        log_group_name, kwargs = self.resolve_lambda_name(log_group_name, **kwargs)
        result = self.client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy=order_by,
            limit=limit,
            descending=True,
            **kwargs,
        )
        return result["logStreams"]

    def get_log_events(self, log_group_name: str, log_stream_name: str, **kwargs):
        """
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_log_events
        """
        log_group_name, kwargs = self.resolve_lambda_name(log_group_name, **kwargs)
        result = self.client.get_log_events(
            logGroupName=log_group_name, logStreamName=log_stream_name, **kwargs
        )
        return result

    def get_latest_log_events(self, log_group_name: str, **kwargs):
        log_group_name, kwargs = self.resolve_lambda_name(log_group_name, **kwargs)
        log_streams = self.describe_log_streams(log_group_name=log_group_name)
        latest_stream_name = log_streams[0]["logStreamName"]
        return self.get_log_events(
            log_group_name=log_group_name, log_stream_name=latest_stream_name
        )

    def find_in_log_message(
        self, log_group_name: str, query_string: str, timeout=10, **kwargs
    ):
        """
        Looks up query_string in the latest logged events

        Args:
            log_group_name:
            query_string:
            timeout: Give up after this many seconds
            **kwargs:

        Returns:
            First found log message containing query_string if one is found;
            otherwise, returns None
        """
        log_group_name, kwargs = self.resolve_lambda_name(log_group_name, **kwargs)
        attempts = 0
        while attempts < timeout:
            latest_stream = self.get_latest_log_events(
                log_group_name=log_group_name, **kwargs
            )
            for event in latest_stream["events"]:
                if query_string in event["message"]:
                    return event["message"]
            time.sleep(1)
            attempts += 1
