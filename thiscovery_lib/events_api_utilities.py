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


class EventsApiClient(tau.ThiscoveryApiClient):

    def __init__(self, env_override=None, correlation_id=None):
        super().__init__(
            env_override=env_override,
            correlation_id=correlation_id,
            api_prefix='events'
        )

    @tau.check_response(HTTPStatus.OK, HTTPStatus.METHOD_NOT_ALLOWED)
    def post_event(self, event):
        return utils.aws_post(
            endpoint_url='v1/event',
            base_url=self.base_url,
            request_body=json.dumps(event),
        )
