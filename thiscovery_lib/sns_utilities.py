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
import thiscovery_lib.utilities as utils


class SnsClient(utils.BaseClient):
    def __init__(self):
        super().__init__('sns')

    def publish(self, message, topic_arn, **kwargs):
        """
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#SNS.Client.publish

        Args:
            message (str): The message you want to send
            topic_arn (str):
            **kwargs:

        Returns:
        """
        return self.client.publish(
            Message=message,
            TopicArn=topic_arn,
            **kwargs
        )

    @staticmethod
    def dict_to_plaintext_list(input_dict):
        indent = "    "
        begin_list = indent
        end_list = "\n"
        list_items = f'\n{indent}'.join([f"<li>{k}: {v}</li>" for k, v in input_dict.items()])
        return f"{begin_list}\n{list_items}\n{end_list}"
