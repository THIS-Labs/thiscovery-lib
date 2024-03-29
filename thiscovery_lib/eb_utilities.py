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
import json
import uuid

import thiscovery_lib.utilities as utils


class EventbridgeClient(utils.BaseClient):
    def __init__(self, profile_name=None):
        super().__init__("events", profile_name=profile_name)
        self.logger = utils.get_logger()

    def put_event(self, thiscovery_event, event_bus_name="thiscovery-event-bus"):
        """
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/events.html#EventBridge.Client.put_events

        Args:
            thiscovery_event (ThiscoveryEvent): instance of ThiscoveryEvent
            event_bus_name:

        Returns:
        """
        entries = [
            {
                "Source": thiscovery_event.event_source,
                "Resources": [],
                "Time": thiscovery_event.event_time,
                "DetailType": thiscovery_event.detail_type,
                "Detail": thiscovery_event.detail,
                "EventBusName": event_bus_name,
            }
        ]
        self.logger.debug(
            "Putting event",
            extra={
                "entries": entries,
            },
        )
        return self.client.put_events(Entries=entries)


class ThiscoveryEvent:
    def __init__(self, event):
        """

        Args:
            event (dict): must contain detail-type and detail (a json-serializable version of event details). It can optionally contain:
                            event_time (string in iso format) - if this is omitted creation time of entity will be used
        """
        try:
            self.detail_type = event["detail-type"]
        except KeyError:
            raise utils.DetailedValueError(
                "mandatory detail-type data not provided", dict()
            )

        try:
            detail = event["detail"]
        except KeyError:
            raise utils.DetailedValueError("mandatory detail data not provided", dict())

        assert isinstance(
            detail, dict
        ), f"detail ({detail}) must be a dictionary, not {type(detail)}"

        self.detail = json.dumps(detail)
        # todo - validate type
        self.event_source = event.get("source", "thiscovery")
        self.event_time = event.get("event_time", str(utils.now_with_tz()))

    def put_event(self, event_bus_name="thiscovery-event-bus"):
        ebc = EventbridgeClient()
        return ebc.put_event(self, event_bus_name)
