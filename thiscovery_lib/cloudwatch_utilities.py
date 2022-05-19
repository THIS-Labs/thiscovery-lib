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
import functools
import json
import uuid

import thiscovery_lib.utilities as utils


class CloudWatchLogsClient(utils.BaseClient):
    def __init__(self):
        super().__init__("logs")

    @staticmethod
    def resolve_lambda_name(stack_name, log_group_name):
        return (
            f"/aws/lambda/{stack_name}-{utils.get_environment_name()}-{log_group_name}"
        )

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
        stack_name = kwargs.pop("stack_name", None)
        if stack_name:
            log_group_name = self.resolve_lambda_name(stack_name, log_group_name)
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
        stack_name = kwargs.pop("stack_name", None)
        if stack_name:
            log_group_name = self.resolve_lambda_name(stack_name, log_group_name)
        result = self.client.get_log_events(
            logGroupName=log_group_name, logStreamName=log_stream_name, **kwargs
        )
        return result

    def get_latest_log_event(self, log_group_name: str, **kwargs):
        stack_name = kwargs.pop("stack_name", None)
        if stack_name:
            log_group_name = self.resolve_lambda_name(stack_name, log_group_name)
        log_streams = self.describe_log_streams(log_group_name=log_group_name)
        latest_stream_name = log_streams[0]["logStreamName"]
        return self.get_log_events(
            log_group_name=log_group_name, log_stream_name=latest_stream_name
        )
