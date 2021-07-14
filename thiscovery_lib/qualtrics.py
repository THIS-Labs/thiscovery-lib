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
import datetime
import requests
import thiscovery_lib.utilities as utils
import warnings

from dateutil import parser


class BaseClient:
    def __init__(self, qualtrics_account_name, api_token=None, correlation_id=None):
        self.base_url = f"https://{qualtrics_account_name}.eu.qualtrics.com/API"
        if api_token is None:
            self.api_token = utils.get_secret("qualtrics-connection")[
                qualtrics_account_name
            ]
        else:
            self.api_token = api_token
        self.logger = utils.get_logger()
        self.correlation_id = correlation_id

    def qualtrics_request(
        self, method, endpoint_url, api_key=None, params=None, data=None
    ):
        if api_key is None:
            api_key = self.api_token

        headers = {
            "content-type": "application/json",
            "Accept": "application/json",
            "x-api-token": api_key,
        }

        self.logger.debug(
            "Qualtrics API call",
            extra={
                "method": method,
                "url": endpoint_url,
                "params": params,
                "json": data,
            },
        )
        response = requests.request(
            method=method,
            url=endpoint_url,
            params=params,
            headers=headers,
            json=data,
        )

        if response.ok:
            return response.json()
        else:
            print(response.text)
            raise utils.DetailedValueError(
                "Call to Qualtrics API failed", details={"response.text": response.text}
            )


class SurveyDefinitionsClient(BaseClient):
    def __init__(
        self, qualtrics_account_name="cambridge", survey_id=None, correlation_id=None
    ):
        """
        Args:
            qualtrics_account_name: defaults to UIS account; alternative value is thisinstitute
            survey_id:
            correlation_id:
        """
        super().__init__(
            qualtrics_account_name=qualtrics_account_name, correlation_id=correlation_id
        )
        self.base_endpoint = f"{self.base_url}/v3/survey-definitions"
        self.survey_endpoint = f"{self.base_endpoint}/{survey_id}"
        self.questions_endpoint = f"{self.survey_endpoint}/questions"
        self.blocks_endpoint = f"{self.survey_endpoint}/blocks"
        self.flow_endpoint = f"{self.survey_endpoint}/flow"

    def refresh_survey_endpoints(self, survey_id):
        self.survey_endpoint = f"{self.base_endpoint}/{survey_id}"
        self.questions_endpoint = f"{self.survey_endpoint}/questions"
        self.blocks_endpoint = f"{self.survey_endpoint}/blocks"
        self.flow_endpoint = f"{self.survey_endpoint}/flow"

    def get_survey(self):
        return self.qualtrics_request("GET", self.survey_endpoint)

    def create_survey(self, survey_name):
        data = {
            "SurveyName": survey_name,
            "Language": "EN-GB",
            "ProjectCategory": "CORE",
        }
        response = self.qualtrics_request("POST", self.base_endpoint, data=data)
        if response["meta"]["httpStatus"] == "200 - OK":
            survey_id = response["result"]["SurveyID"]
            self.refresh_survey_endpoints(survey_id)
            return survey_id
        else:
            raise utils.DetailedValueError(
                "API call to Qualtrics create survey method failed",
                details={"response": response},
            )

    def create_question(self, data):
        return self.qualtrics_request("POST", self.questions_endpoint, data=data)

    def update_question(self, question_id, data):
        endpoint = f"{self.questions_endpoint}/{question_id}"
        return self.qualtrics_request("PUT", endpoint, data=data)

    def delete_question(self, question_id):
        endpoint = f"{self.questions_endpoint}/{question_id}"
        return self.qualtrics_request("DELETE", endpoint)

    def create_block(self, data):
        return self.qualtrics_request("POST", self.blocks_endpoint, data=data)

    def update_block(self, block_id, data):
        endpoint = f"{self.blocks_endpoint}/{block_id}"
        return self.qualtrics_request("PUT", endpoint, data=data)

    def delete_block(self, block_id):
        endpoint = f"{self.blocks_endpoint}/{block_id}"
        return self.qualtrics_request("DELETE", endpoint)

    def update_flow(self, data):
        return self.qualtrics_request("PUT", self.flow_endpoint, data=data)


class DistributionsClient(BaseClient):
    def __init__(self, qualtrics_account_name="cambridge", correlation_id=None):
        """
        Args:
            qualtrics_account_name: defaults to UIS account; alternative value is thisinstitute
            correlation_id:
        """
        super().__init__(
            qualtrics_account_name=qualtrics_account_name, correlation_id=correlation_id
        )
        self.base_endpoint = f"{self.base_url}/v3/distributions"

    def _create_distribution(self, data):
        """
        https://api.qualtrics.com/api-reference/reference/distributions.json/paths/~1distributions/post
        """
        return self.qualtrics_request("POST", self.base_endpoint, data=data)

    def list_distributions(self, survey_id: str, **kwargs) -> list[dict]:
        """
        https://api.qualtrics.com/api-reference/reference/distributions.json/paths/~1distributions/get

        Args:
            survey_id: The ID of the survey to which the distribution belongs.
            **kwargs:

        Returns:
        """
        params = {
            "surveyId": survey_id,
        }
        params.update(kwargs)
        response = self.qualtrics_request("GET", self.base_endpoint, params=params)
        assert (
            response["meta"]["httpStatus"] == "200 - OK"
        ), f"Qualtrics API call failed with response: {response}"
        return response["result"]["elements"]

    def create_individual_links(self, survey_id, contact_list_id, **kwargs):
        now = datetime.datetime.now()
        now_str = now.strftime("%Y-%m-%d_%H:%M:%S")
        expiration = now + datetime.timedelta(days=90)
        expiration_str = expiration.strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "surveyId": survey_id,
            "linkType": "Individual",
            "description": f"distribution_{survey_id}_{now_str}",
            "action": "CreateDistribution",
            "expirationDate": expiration_str,
            "mailingListId": contact_list_id,
        }
        data.update(**kwargs)
        return self._create_distribution(data=data)

    def list_distribution_links(self, distribution_id, survey_id):
        """
        https://api.qualtrics.com/api-reference/reference/distributions.json/paths/~1distributions~1%7BdistributionId%7D~1links/get
        """
        warnings.warn(
            "This method will be deprecated soon; use list_distribution_links_v2 instead",
            PendingDeprecationWarning,
        )
        endpoint = f"{self.base_endpoint}/{distribution_id}/links"
        params = {
            "surveyId": survey_id,
        }
        result = self.qualtrics_request("GET", endpoint, params=params)

        # workaround to fix invalid links; contacted Qualtrics about this; removed when issue is solved
        for r in result["result"]["elements"]:
            r["link"] = r["link"].replace("qualtrics.com//jfe", "qualtrics.com/jfe")

        return result

    def list_distribution_links_v2(self, distribution_id, survey_id):
        """
        Extends previous version by dealing with pagination to return more than 100 links
        https://api.qualtrics.com/api-reference/reference/distributions.json/paths/~1distributions~1%7BdistributionId%7D~1links/get
        """
        endpoint = f"{self.base_endpoint}/{distribution_id}/links"
        params = {
            "surveyId": survey_id,
        }
        elements = list()
        while True:
            r = self.qualtrics_request("GET", endpoint, params=params)
            assert (
                r["meta"]["httpStatus"] == "200 - OK"
            ), f"Call to Qualtrics API failed with response: {result}"

            result = r["result"]
            # workaround to fix invalid links; contacted Qualtrics about this; removed when issue is solved
            elem = result["elements"]
            for e in elem:
                e["link"] = e["link"].replace("qualtrics.com//jfe", "qualtrics.com/jfe")

            elements += elem

            next_page = result.get("nextPage")
            if next_page:
                skip_token = next_page.split("skipToken=")[-1]
                params.update(skipToken=skip_token)
            else:
                break

        return elements

    def delete_distribution(self, distribution_id):
        """
        https://api.qualtrics.com/api-reference/reference/distributions.json/paths/~1distributions~1%7BdistributionId%7D/delete
        """
        endpoint = f"{self.base_endpoint}/{distribution_id}"
        return self.qualtrics_request("DELETE", endpoint)


class ResponsesClient(BaseClient):
    def __init__(
        self, survey_id, qualtrics_account_name="cambridge", correlation_id=None
    ):
        """
        Args:
            survey_id:
            qualtrics_account_name: defaults to UIS account; alternative value is thisinstitute
            correlation_id:
        """
        super().__init__(
            qualtrics_account_name=qualtrics_account_name, correlation_id=correlation_id
        )
        self.base_endpoint = f"{self.base_url}/v3/surveys/{survey_id}"

    def retrieve_survey_response_schema(self):
        """
        https://api.qualtrics.com/api-reference/reference/singleResponses.json/paths/~1surveys~1%7BsurveyId%7D~1response-schema/get
        """
        url = f"{self.base_endpoint}/response-schema"
        response = self.qualtrics_request("GET", endpoint_url=url)
        assert (
            response["meta"]["httpStatus"] == "200 - OK"
        ), f"Qualtrics API call failed with response: {response}"
        return response

    def retrieve_response(self, response_id):
        """
        https://api.qualtrics.com/api-reference/reference/singleResponses.json/paths/~1surveys~1%7BsurveyId%7D~1responses~1%7BresponseId%7D/get
        """
        url = f"{self.base_endpoint}/responses/{response_id}"
        response = self.qualtrics_request("GET", endpoint_url=url)
        assert (
            response["meta"]["httpStatus"] == "200 - OK"
        ), f"Qualtrics API call failed with response: {response}"
        return response


class DirectoriesClient(BaseClient):
    def __init__(self, qualtrics_account_name="cambridge", correlation_id=None):
        """
        Args:
            qualtrics_account_name: defaults to UIS account; alternative value is thisinstitute
            correlation_id:
        """
        super().__init__(
            qualtrics_account_name=qualtrics_account_name, correlation_id=correlation_id
        )
        self.base_endpoint = f"{self.base_url}/v3/directories"

    def list_directories(self):
        return self.qualtrics_request("GET", self.base_endpoint)


class MailingListsClient(BaseClient):
    def __init__(
        self, qualtrics_account_name="cambridge", directory_id=None, correlation_id=None
    ):
        """
        Args:
            qualtrics_account_name: defaults to UIS account; alternative value is thisinstitute
            correlation_id:
        """
        super().__init__(
            qualtrics_account_name=qualtrics_account_name, correlation_id=correlation_id
        )
        self.base_endpoint = (
            f"{self.base_url}/v3/directories/{directory_id}/mailinglists"
        )

    def list_mailing_lists(self):
        return self.qualtrics_request("GET", self.base_endpoint)

    def create_mailing_list(self, name, owner_id):
        return self.qualtrics_request(
            "POST",
            self.base_endpoint,
            data={
                "name": name,
                "ownerId": owner_id,
            },
        )


def qualtrics2thiscovery_timestamp(qualtrics_datetime_string):
    return str(parser.parse(qualtrics_datetime_string))
