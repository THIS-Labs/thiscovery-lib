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

import thiscovery_lib.thiscovery_api_utilities as tau
import thiscovery_lib.utilities as utils


class InterviewsApiClient(tau.ThiscoveryApiClient):

    def __init__(self, env_override=None, correlation_id=None):
        super(InterviewsApiClient, self).__init__(
            correlation_id=correlation_id,
            env_override=env_override,
            api_prefix='interviews',
        )

    @tau.check_response(HTTPStatus.OK)
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
        return utils.aws_request(
            method='GET',
            endpoint_url='v1/appointments-by-type',
            base_url=self.base_url,
            data=json.dumps(body),
        )

    @tau.check_response(HTTPStatus.OK)
    def set_interview_url(self, appointment_id, interview_url, event_type, **kwargs):
        body = {
            'appointment_id': appointment_id,
            'interview_url': interview_url,
            'event_type': event_type,
            'correlation_id': self.correlation_id,
            **kwargs,
        }
        self.logger.debug("Calling interviews API set-interview-url endpoint", extra={'body': body})
        return utils.aws_request(
            method='PUT',
            endpoint_url='v1/set-interview-url',
            base_url=self.base_url,
            data=json.dumps(body),
        )
