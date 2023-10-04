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
import os
from thiscovery_lib.utilities import (
    DetailedValueError,
    get_file_as_string,
)

# region Country code/name processing
def append_country_name_to_list(entity_list):
    for entity in entity_list:
        append_country_name(entity)
    return entity_list


def append_country_name(entity):
    country_code = entity.get("country_code", "")
    entity["country_name"] = get_country_name(country_code)

    birth_country_code = entity.get("birth_country_code", "")
    entity["birth_country_name"] = get_country_name(birth_country_code)


def load_countries():
    country_list_filename = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "countries.json"
    )
    country_list = json.loads(get_file_as_string(country_list_filename))
    countries_dict = {}
    for country in country_list:
        countries_dict[country["Code"]] = country["Name"]
    return countries_dict


def get_country_name(country_code):
    try:
        return countries.get(country_code)
    except KeyError as err:
        errorjson = {"country_code": country_code}
        raise DetailedValueError("invalid country code", errorjson)


countries = load_countries()
# endregion
