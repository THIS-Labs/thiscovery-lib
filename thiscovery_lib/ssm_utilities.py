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
import thiscovery_lib.utilities as utils
from http import HTTPStatus


class SsmClient(utils.BaseClient):
    def __init__(self):
        super().__init__("ssm")

    def get_parameter(self, name: str) -> dict[str, dict]:
        """
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.get_parameter

        Args:
            name (str): Name of the parameters for which you want to query information

        Returns:
        """
        param_name = f"{utils.get_aws_namespace()}{name}"
        response = self.client.get_parameter(Name=param_name)
        assert (
            response["ResponseMetadata"]["HTTPStatusCode"] == HTTPStatus.OK
        ), f"Call to SSM client failed with response: {response}"
        return json.loads(response["Parameter"]["Value"])

    def get_parameters(self, names: list) -> dict[str, list]:
        """
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.get_parameters

        Args:
            names (list): Names of the parameters for which you want to query information

        Returns:
        """
        namespace = utils.get_aws_namespace()
        return self.client.get_parameters(
            Names=[f"{namespace}{name}" for name in names]
        )
