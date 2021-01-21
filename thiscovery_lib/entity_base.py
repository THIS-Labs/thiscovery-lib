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
import uuid
import json
import jsons
from abc import ABC

from thiscovery_lib.utilities import now_with_tz, validate_uuid, validate_utc_datetime, DetailedValueError


class EntityBase(ABC):
    """
    EntityBase is an abstract base class for all persisted entities that include id (uuid as string) and created, modified (dates as strings)
    """
    def __init__(self, entity_json=[], correlation_id=None):
        if 'id' in entity_json:
            try:
                self.id = validate_uuid(entity_json['id'])
            except DetailedValueError as err:
                err.add_correlation_id(correlation_id)
                raise err
        else:
            self.id = str(uuid.uuid4())

        if 'created' in entity_json:
            try:
                self.created = validate_utc_datetime(entity_json['created'])
            except DetailedValueError as err:
                err.add_correlation_id(correlation_id)
                raise err
        else:
            self.created = str(now_with_tz())

        if 'modified' in entity_json:
            try:
                self.modified = validate_utc_datetime(entity_json['modified'])
            except DetailedValueError as err:
                err.add_correlation_id(correlation_id)
                raise err
        else:
            self.modified = str(now_with_tz())

    def to_json(self):
        # https://stackoverflow.com/questions/3768895/how-to-make-a-class-json-serializable
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def to_dict(self):
        return jsons.dump(self, strip_class_variables=True)
