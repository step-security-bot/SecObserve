from unittests.access_control.api.test_authorization import (
    APITest,
    TestAuthorizationBase,
)


class TestAuthorizationGeneralRules(TestAuthorizationBase):
    def test_authorization_general_rules(self):
        # --- general_rules ---

        expected_data = "OrderedDict({'count': 1, 'next': None, 'previous': None, 'results': [OrderedDict({'id': 3, 'name': 'db_general_rule', 'description': '', 'scanner_prefix': '', 'title': '', 'description_observation': '', 'origin_component_name_version': '', 'origin_docker_image_name_tag': '', 'origin_endpoint_url': '', 'origin_service_name': '', 'origin_source_file': '', 'origin_cloud_qualified_resource': '', 'new_severity': '', 'new_status': '', 'enabled': True, 'parser': 1})]})"
        self._test_api(
            APITest(
                "db_internal_write",
                "get",
                "/api/general_rules/",
                None,
                200,
                expected_data,
            )
        )

        expected_data = "{'message': 'No Rule matches the given query.'}"
        self._test_api(
            APITest(
                "db_internal_write",
                "get",
                "/api/general_rules/1/",
                None,
                404,
                expected_data,
            )
        )

        expected_data = "{'id': 3, 'name': 'db_general_rule', 'description': '', 'scanner_prefix': '', 'title': '', 'description_observation': '', 'origin_component_name_version': '', 'origin_docker_image_name_tag': '', 'origin_endpoint_url': '', 'origin_service_name': '', 'origin_source_file': '', 'origin_cloud_qualified_resource': '', 'new_severity': '', 'new_status': '', 'enabled': True, 'parser': 1}"
        self._test_api(
            APITest(
                "db_internal_write",
                "get",
                "/api/general_rules/3/",
                None,
                200,
                expected_data,
            )
        )

        post_data = {"name": "string", "parser": 1}
        expected_data = (
            "{'message': 'You do not have permission to perform this action.'}"
        )
        self._test_api(
            APITest(
                "db_internal_write",
                "post",
                "/api/general_rules/",
                post_data,
                403,
                expected_data,
            )
        )

        expected_data = "{'id': 4, 'name': 'string', 'description': '', 'scanner_prefix': '', 'title': '', 'description_observation': '', 'origin_component_name_version': '', 'origin_docker_image_name_tag': '', 'origin_endpoint_url': '', 'origin_service_name': '', 'origin_source_file': '', 'origin_cloud_qualified_resource': '', 'new_severity': '', 'new_status': '', 'enabled': True, 'parser': 1}"
        self._test_api(
            APITest(
                "db_admin", "post", "/api/general_rules/", post_data, 201, expected_data
            )
        )

        expected_data = (
            "{'message': 'You do not have permission to perform this action.'}"
        )
        self._test_api(
            APITest(
                "db_internal_write",
                "patch",
                "/api/general_rules/3/",
                {"name": "changed"},
                403,
                expected_data,
            )
        )

        expected_data = "{'id': 3, 'name': 'changed', 'description': '', 'scanner_prefix': 'also_changed', 'title': '', 'description_observation': '', 'origin_component_name_version': '', 'origin_docker_image_name_tag': '', 'origin_endpoint_url': '', 'origin_service_name': '', 'origin_source_file': '', 'origin_cloud_qualified_resource': '', 'new_severity': '', 'new_status': '', 'enabled': True, 'parser': 1}"
        self._test_api(
            APITest(
                "db_admin",
                "patch",
                "/api/general_rules/3/",
                {"name": "changed", "scanner_prefix": "also_changed"},
                200,
                expected_data,
            )
        )

        expected_data = (
            "{'message': 'You do not have permission to perform this action.'}"
        )
        self._test_api(
            APITest(
                "db_internal_write",
                "delete",
                "/api/general_rules/3/",
                None,
                403,
                expected_data,
            )
        )

        expected_data = "None"
        self._test_api(
            APITest(
                "db_admin", "delete", "/api/general_rules/3/", None, 204, expected_data
            )
        )
