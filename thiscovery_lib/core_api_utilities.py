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
import warnings
from http import HTTPStatus

import thiscovery_lib.thiscovery_api_utilities as tau
import thiscovery_lib.utilities as utils


class CoreApiClient(tau.ThiscoveryApiClient):
    @tau.check_response(HTTPStatus.OK)
    def ping(self):
        return utils.aws_get("v1/ping", self.base_url)

    @tau.check_response(HTTPStatus.OK, HTTPStatus.NOT_FOUND)
    def get_user_by_user_id(self, user_id):
        return utils.aws_get(
            endpoint_url=f"v1/userv2/{user_id}", base_url=self.base_url
        )

    @tau.process_response
    @tau.check_response(HTTPStatus.OK)
    def get_user_by_email(self, email):
        return utils.aws_get("v1/user", self.base_url, params={"email": email})

    def get_user_id_by_email(self, email):
        user = self.get_user_by_email(email=email)
        return user["id"]

    @tau.process_response
    @tau.check_response(HTTPStatus.OK)
    def get_user_by_anon_project_specific_user_id(self, anon_project_specific_user_id):
        return utils.aws_get(
            "v1/user",
            self.base_url,
            params={"anon_project_specific_user_id": anon_project_specific_user_id},
        )

    @tau.check_response(HTTPStatus.NO_CONTENT)
    def patch_user(self, user_id: str, jsonpatch: list):
        return utils.aws_patch(
            f"v1/user/{user_id}",
            self.base_url,
            request_body=json.dumps(jsonpatch),
        )

    @tau.check_response(HTTPStatus.CREATED)
    def post_user(self, user_dict: dict) -> dict:
        return utils.aws_post(
            f"v1/user",
            self.base_url,
            request_body=json.dumps(user_dict),
        )

    @tau.check_response(HTTPStatus.NO_CONTENT)
    def patch_group_email_despatch(self, group_email_despatch_id: str, jsonpatch: list):
        return utils.aws_patch(
            f"v1/groupemaildespatch/{group_email_despatch_id}",
            self.base_url,
            request_body=json.dumps(jsonpatch),
        )

    @tau.check_response(HTTPStatus.OK)
    def update_group_email_despatch_send_start_date(self, group_email_despatch_id: str):
        return utils.aws_post(
            f"v1/updategroupemaildespatchstart/{group_email_despatch_id}/",
            self.base_url,
        )

    @tau.check_response(HTTPStatus.OK)
    def update_group_email_despatch_send_complete_date(
        self, group_email_despatch_id: str
    ):
        return utils.aws_post(
            f"v1/updategroupemaildespatchcomplete/{group_email_despatch_id}/",
            self.base_url,
        )

    @tau.check_response(HTTPStatus.NO_CONTENT)
    def delete_group_email_despatch(self, group_email_despatch_id: str):
        return utils.aws_delete(
            f"v1/groupemaildespatch/{group_email_despatch_id}", self.base_url
        )

    @tau.check_response(HTTPStatus.OK, HTTPStatus.NOT_FOUND)
    def get_group_email_despatch(self, group_email_despatch_id):
        """
        Args:
            group_email_despatch_id: uuid of group_email_despatch_id
        Returns:
            A group email despatch
        """

        return utils.aws_get(
            f"v1/groupemaildespatch/{group_email_despatch_id}",
            self.base_url,
        )

    @tau.check_response(HTTPStatus.CREATED)
    def post_group_email_despatch(self, group_email_despatch_dict: dict) -> dict:
        return utils.aws_post(
            f"v1/groupemaildespatch",
            self.base_url,
            request_body=json.dumps(group_email_despatch_dict),
        )

    @tau.process_response
    @tau.check_response(HTTPStatus.OK)
    def get_projects(self):
        return utils.aws_get("v1/project", self.base_url, params={})

    @tau.process_response
    @tau.check_response(HTTPStatus.OK)
    def _get_userprojects(self, **params):
        return utils.aws_get("v1/userproject", self.base_url, params=params)

    def get_userprojects(self, user_id):
        return self._get_userprojects(user_id=user_id)

    def get_userprojects_from_anon_user_task_id(self, anon_user_task_id):
        return self._get_userprojects(anon_user_task_id=anon_user_task_id)

    @tau.process_response
    @tau.check_response(HTTPStatus.OK)
    def list_users_by_project(self, project_id):
        return utils.aws_get(
            "v1/list-project-users", self.base_url, params={"project_id": project_id}
        )

    @tau.process_response
    @tau.check_response(HTTPStatus.OK)
    def _list_user_tasks(self, query_parameter):
        return utils.aws_get("v1/usertask", self.base_url, params=query_parameter)

    def list_user_tasks(self, query_parameter):
        """
        Args:
            query_parameter (dict): use either 'user_id' or 'anon_user_task_id' as key

        Returns:
        """
        user_task_info = self._list_user_tasks(query_parameter=query_parameter)
        if isinstance(user_task_info, dict):
            return [user_task_info]
        else:  # user_task_info is list
            return user_task_info

    def get_user_task_id_for_project(self, user_id, project_task_id):
        result = self.list_user_tasks(query_parameter={"user_id": user_id})
        for user_task in result:
            if user_task["project_task_id"] == project_task_id:
                return user_task["user_task_id"]

    def get_user_task_from_anon_user_task_id(self, anon_user_task_id):
        result = self.list_user_tasks(
            query_parameter={"anon_user_task_id": anon_user_task_id}
        )
        for user_task in result:
            if user_task["anon_user_task_id"] == anon_user_task_id:
                return user_task

    @tau.check_response(HTTPStatus.NO_CONTENT)
    def set_user_task_completed(self, user_task_id=None, anon_user_task_id=None):
        if user_task_id is not None:
            return utils.aws_request(
                "PUT",
                "v1/user-task-completed",
                self.base_url,
                params={"user_task_id": user_task_id},
            )
        elif anon_user_task_id is not None:
            return utils.aws_request(
                "PUT",
                "v1/user-task-completed",
                self.base_url,
                params={"anon_user_task_id": anon_user_task_id},
            )

    @tau.check_response(HTTPStatus.CREATED)
    def create_user_task(self, user_task_data):
        return utils.aws_request(
            "POST", "v1/usertask", self.base_url, data=json.dumps(user_task_data)
        )

    def get_project_from_project_task_id(self, project_task_id):
        project_list = self.get_projects()
        for project in project_list:
            for t in project["tasks"]:
                if t["id"] == project_task_id:
                    return project
        raise utils.ObjectDoesNotExistError(
            f"Project task {project_task_id} not found", details={}
        )

    @tau.process_response
    @tau.check_response(HTTPStatus.OK)
    def _list_group_email_despatch_users(self, group_email_despatch_id):
        return utils.aws_get(
            "v1/list-group-email-despatch-users",
            self.base_url,
            params={"group_email_despatch": group_email_despatch_id},
        )

    def list_group_email_despatch_users(self, group_email_despatch_id):
        """
        Args:
            group_email_despatch_id: uuid of group_email_despatch_id
        Returns:
            A list of user_ids
        """
        user_ids = self._list_group_email_despatch_users(
            group_email_despatch_id=group_email_despatch_id
        )

        return user_ids

    @tau.process_response
    @tau.check_response(HTTPStatus.OK)
    def list_user_lists(self):
        return utils.aws_get("v1/userlist", self.base_url, params={})

    @tau.check_response(HTTPStatus.CREATED)
    def create_user_email_despatch(self, user_email_despatch_data):
        return utils.aws_post(
            "v1/useremaildespatch",
            self.base_url,
            request_body=json.dumps(user_email_despatch_data),
        )
