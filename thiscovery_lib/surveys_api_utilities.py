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


class SurveysApiClient(tau.ThiscoveryApiClient):
    def __init__(self, env_override=None, correlation_id=None):
        super(SurveysApiClient, self).__init__(
            env_override=env_override,
            correlation_id=correlation_id,
            api_prefix="surveys",
        )

    @tau.check_response(HTTPStatus.OK, HTTPStatus.METHOD_NOT_ALLOWED)
    def put_response(self, **kwargs):
        body = {
            **kwargs,
        }
        self.logger.debug(
            "Calling surveys API put_response_api endpoint", extra={"body": body}
        )
        return utils.aws_request(
            method="PUT",
            endpoint_url="v1/response",
            base_url=self.base_url,
            data=json.dumps(body),
        )

    @tau.process_response
    @tau.check_response(HTTPStatus.OK)
    def get_personal_link(
        self, survey_id, anon_project_specific_user_id, account="cambridge"
    ):
        return utils.aws_get(
            endpoint_url="v1/personal-link",
            base_url=self.base_url,
            params={
                "survey_id": survey_id,
                "anon_project_specific_user_id": anon_project_specific_user_id,
                "account": account,
            },
        )

    @tau.process_response
    @tau.check_response(HTTPStatus.OK, HTTPStatus.NOT_FOUND)
    def get_user_interview_tasks(self, anon_user_task_id):
        return utils.aws_get(
            endpoint_url="v1/user-interview-tasks",
            base_url=self.base_url,
            params={
                "anon_user_task_id": anon_user_task_id,
            },
        )
