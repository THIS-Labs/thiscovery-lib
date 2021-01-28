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


class CoreApiClient(tau.ThiscoveryApiClient):

    @tau.process_response
    @tau.check_response(HTTPStatus.OK)
    def get_user_by_email(self, email):
        return utils.aws_get('v1/user', self.base_url, params={'email': email})

    def get_user_id_by_email(self, email):
        user = self.get_user_by_email(email=email)
        return user['id']

    @tau.process_response
    @tau.check_response(HTTPStatus.OK)
    def get_projects(self):
        return utils.aws_get('v1/project', self.base_url, params={})

    @tau.process_response
    @tau.check_response(HTTPStatus.OK)
    def get_userprojects(self, user_id):
        return utils.aws_get('v1/userproject', self.base_url, params={'user_id': user_id})

    @tau.process_response
    @tau.check_response(HTTPStatus.OK)
    def list_users_by_project(self, project_id):
        return utils.aws_get('v1/list-project-users', self.base_url, params={'project_id': project_id})

    @tau.process_response
    @tau.check_response(HTTPStatus.OK)
    def _list_user_tasks(self, query_parameter):
        return utils.aws_get('v1/usertask', self.base_url, params=query_parameter)

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
        result = self.list_user_tasks(query_parameter={'user_id': user_id})
        for user_task in result:
            if user_task['project_task_id'] == project_task_id:
                return user_task['user_task_id']

    def get_user_task_from_anon_user_task_id(self, anon_user_task_id):
        result = self.list_user_tasks(query_parameter={
            'anon_user_task_id': anon_user_task_id
        })
        for user_task in result:
            if user_task['anon_user_task_id'] == anon_user_task_id:
                return user_task

    @tau.check_response(HTTPStatus.OK)
    def set_user_task_completed(self, user_task_id=None, anon_user_task_id=None):
        if user_task_id is not None:
            return utils.aws_request('PUT', 'v1/user-task-completed', self.base_url, params={'user_task_id': user_task_id})
        elif anon_user_task_id is not None:
            return utils.aws_request('PUT', 'v1/user-task-completed', self.base_url, params={
                'anon_user_task_id': anon_user_task_id
            })

    @tau.check_response(HTTPStatus.NO_CONTENT)
    def send_transactional_email(self, template_name, **kwargs):
        """
        Calls the send-transactional-email endpoint. Appends 'NA_' to template_name
        if running_unit_tests() returns True to prevent unittest emails being sent

        Args:
            template_name:
            **kwargs: Either to_recipient_id or to_recipient_email must be present

        Returns:
        """
        email_dict = {
            "template_name": template_name,
            **kwargs
        }
        if utils.running_unit_tests():
            email_dict['template_name'] = f'NA_{template_name}'
        self.logger.debug("Transactional email API call", extra={'email_dict': email_dict})
        return utils.aws_post('v1/send-transactional-email', self.base_url, request_body=json.dumps(email_dict))

    def get_project_from_project_task_id(self, project_task_id):
        project_list = self.get_projects()
        for project in project_list:
            for t in project['tasks']:
                if t['id'] == project_task_id:
                    return project
        raise utils.ObjectDoesNotExistError(f'Project task {project_task_id} not found', details={})
