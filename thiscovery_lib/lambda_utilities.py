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
import base64
import json
import thiscovery_lib.utilities as utils


class Lambda(utils.BaseClient):

    def __init__(self, stack_name='thiscovery-core', correlation_id=None):
        super().__init__('lambda', correlation_id=correlation_id)
        super().get_namespace()
        self.stack_name = stack_name

    def invoke(self, function_name, function_name_verbatim=False, invocation_type='RequestResponse', payload=dict()):
        """
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.invoke
        """
        payload = {'correlation_id': self.correlation_id, **payload}
        if function_name_verbatim:
            full_name = function_name
        else:
            full_name = '-'.join([self.stack_name, self.aws_namespace, function_name])

        response = self.client.invoke(
            FunctionName=full_name,
            InvocationType=invocation_type,
            LogType='Tail',
            Payload=json.dumps(payload).encode('utf-8'),
        )
        try:
            log_result_str = base64.b64decode(response['LogResult']).decode('utf-8')
        except KeyError:
            response['LogResult'] = 'None'
        else:
            log_result_list = log_result_str.split('\n')
            log_result = [json.loads(x.split(';1m')[1]) for x in log_result_list if ';1m' in x]
            response['LogResult'] = log_result
        try:
            response['Payload'] = json.loads(response['Payload'].read().decode('utf-8'))
        except json.decoder.JSONDecodeError:
            response['Payload'] = 'None'
        return response

    def list_functions(self):
        """
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.list_functions
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Paginator.ListFunctions

        Returns:
        """
        funcs = list()
        paginator = self.client.get_paginator('list_functions')
        for response in paginator.paginate():
            assert response['ResponseMetadata']['HTTPStatusCode'] == 200, f'call to boto3.client.list_functions failed with response: {response}'
            funcs += response['Functions']
        return funcs
