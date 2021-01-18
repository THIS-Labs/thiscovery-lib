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
import json
from http import HTTPStatus

import thiscovery_lib.utilities as utils


class InterviewsApiClient:

    def __init__(self, env_override=None, correlation_id=None):
        self.correlation_id = correlation_id
        self.logger = utils.get_logger()
        if env_override:
            env_name = env_override
        else:
            env_name = utils.get_environment_name()
        if env_name == 'prod':
            self.base_url = 'https://interviews-api.thiscovery.org/'
        else:
            self.base_url = f'https://{env_name}-interviews-api.thiscovery.org/'

    def get_appointments_by_type_ids(self, appointment_type_ids):
        """
        Args:
            appointment_type_ids (list):

        Returns:
        """
        body = {
            'type_ids': appointment_type_ids,
        }
        self.logger.debug("Calling interviews API appointments-by-type endpoint", extra={
            'body': body
        })
        result = utils.aws_request(
            method='GET',
            endpoint_url='v1/appointments-by-type',
            base_url=self.base_url,
            data=json.dumps(body),
        )
        assert result['statusCode'] == HTTPStatus.OK, f'Call to interviews API returned error: {result}'
        return result

    def set_interview_url(self, appointment_id, interview_url, event_type, **kwargs):
        body = {
            'appointment_id': appointment_id,
            'interview_url': interview_url,
            'event_type': event_type,
            'correlation_id': self.correlation_id,
            **kwargs,
        }
        self.logger.debug("Calling interviews API set-interview-url endpoint", extra={'body': body})
        result = utils.aws_request(
            method='PUT',
            endpoint_url='v1/set-interview-url',
            base_url=self.base_url,
            data=json.dumps(body),
        )
        assert result['statusCode'] == HTTPStatus.OK, f'Call to interviews API returned error: {result}'
        return result
