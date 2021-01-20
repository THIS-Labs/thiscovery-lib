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


class CoreApiClient:

    def __init__(self, correlation_id=None, env_overwrite=None):
        self.correlation_id = correlation_id
        self.logger = utils.get_logger()
        if env_overwrite:
            env_name = env_overwrite
        else:
            env_name = utils.get_environment_name()
        if env_name == 'prod':
            self.base_url = 'https://api.thiscovery.org/'
        else:
            self.base_url = f'https://{env_name}-api.thiscovery.org/'

    def get_user_by_email(self, email):
        # todo: similar code is used in stack s3-to-sdhs; adapt that stack to use this client
        result = utils.aws_get('v1/user', self.base_url, params={'email': email})
        assert result['statusCode'] == HTTPStatus.OK, f'Call to core API returned error: {result}'
        return json.loads(result['body'])

    def get_user_id_by_email(self, email):
        user = self.get_user_by_email(email=email)
        return user['id']

    def get_projects(self):
        result = utils.aws_get('v1/project', self.base_url, params={})
        assert result['statusCode'] == HTTPStatus.OK, f'Call to core API returned error: {result}'
        return json.loads(result['body'])

    def get_userprojects(self, user_id):
        result = utils.aws_get('v1/userproject', self.base_url, params={'user_id': user_id})
        assert result['statusCode'] == HTTPStatus.OK, f'Call to core API returned error: {result}'
        return json.loads(result['body'])

    def list_users_by_project(self, project_id):
        result = utils.aws_get('v1/list-project-users', self.base_url, params={'project_id': project_id})
        assert result['statusCode'] == HTTPStatus.OK, f'Call to core API returned error: {result}'
        return json.loads(result['body'])

    def list_user_tasks(self, query_parameter):
        """
        Args:
            query_parameter (dict): use either 'user_id' or 'anon_user_task_id' as key

        Returns:
        """
        result = utils.aws_get('v1/usertask', self.base_url, params=query_parameter)
        assert result['statusCode'] == HTTPStatus.OK, f'Call to core API returned error: {result}'
        user_task_info = json.loads(result['body'])
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

    def set_user_task_completed(self, user_task_id=None, anon_user_task_id=None):
        if user_task_id is not None:
            result = utils.aws_request('PUT', 'v1/user-task-completed', self.base_url, params={'user_task_id': user_task_id})
        elif anon_user_task_id is not None:
            result = utils.aws_request('PUT', 'v1/user-task-completed', self.base_url, params={
                'anon_user_task_id': anon_user_task_id
            })
        assert result['statusCode'] == HTTPStatus.NO_CONTENT, f'Call to core API returned error: {result}'
        return result

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
        result = utils.aws_post('v1/send-transactional-email', self.base_url, request_body=json.dumps(email_dict))
        assert result['statusCode'] == HTTPStatus.NO_CONTENT, f'Call to core API returned error: {result}'
        return result

    def get_project_from_project_task_id(self, project_task_id):
        project_list = self.get_projects()
        for project in project_list:
            for t in project['tasks']:
                if t['id'] == project_task_id:
                    return project
        raise utils.ObjectDoesNotExistError(f'Project task {project_task_id} not found', details={})
