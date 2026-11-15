from unittest.mock import Mock

import requests
from django.test import SimpleTestCase, override_settings

from .moysklad import MoySkladClient, MoySkladError


class MoySkladClientTests(SimpleTestCase):
    @override_settings(MOYSKLAD_ACCESS_TOKEN='test-token')
    def test_lists_warehouses_and_sends_bearer_token(self):
        response = Mock()
        response.json.return_value = {'rows': [{'id': 'ekb-id', 'name': 'Екатеринбург'}]}
        response.raise_for_status.return_value = None
        session = Mock()
        session.get.return_value = response

        warehouses = MoySkladClient(session=session).list_warehouses()

        self.assertEqual([(item.id, item.name) for item in warehouses], [('ekb-id', 'Екатеринбург')])
        url = session.get.call_args.args[0]
        self.assertEqual(url, 'https://api.moysklad.ru/api/remap/1.2/entity/store')
        self.assertEqual(session.get.call_args.kwargs['headers']['Authorization'], 'Bearer test-token')
        self.assertEqual(session.get.call_args.kwargs['headers']['Accept'], 'application/json;charset=utf-8')
        self.assertEqual(session.get.call_args.kwargs['params'], {'limit': 100, 'offset': 0})

    @override_settings(MOYSKLAD_ACCESS_TOKEN='')
    def test_token_is_required_before_network_request(self):
        session = Mock()
        with self.assertRaisesMessage(MoySkladError, 'MOYSKLAD_ACCESS_TOKEN'):
            MoySkladClient(session=session).list_warehouses()
        session.get.assert_not_called()

    @override_settings(MOYSKLAD_ACCESS_TOKEN='test-token')
    def test_follows_collection_pages(self):
        first = Mock()
        first.raise_for_status.return_value = None
        first.json.return_value = {'rows': [{'id': f'id-{number}', 'name': f'Склад {number}'} for number in range(100)]}
        second = Mock()
        second.raise_for_status.return_value = None
        second.json.return_value = {'rows': [{'id': 'last', 'name': 'Последний'}]}
        session = Mock()
        session.get.side_effect = [first, second]

        warehouses = MoySkladClient(session=session).list_warehouses()

        self.assertEqual(len(warehouses), 101)
        self.assertEqual(session.get.call_args_list[1].kwargs['params']['offset'], 100)

    @override_settings(MOYSKLAD_ACCESS_TOKEN='test-token')
    def test_includes_safe_api_error_detail(self):
        response = Mock(status_code=400)
        response.json.return_value = {'errors': [{'error': 'Недопустимый параметр'}]}
        response.raise_for_status.side_effect = requests.HTTPError(response=response)
        session = Mock()
        session.get.return_value = response

        with self.assertRaisesMessage(MoySkladError, 'Недопустимый параметр'):
            MoySkladClient(session=session).list_warehouses()
