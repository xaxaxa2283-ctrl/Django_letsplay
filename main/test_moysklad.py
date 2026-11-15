from unittest.mock import Mock

import requests
from django.test import SimpleTestCase, override_settings

from .moysklad import MoySkladClient, MoySkladError
from .management.commands.moysklad_match_preview import normalized_tokens, score


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
    def test_reads_assortment_and_converts_minor_units_to_rubles(self):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            'rows': [{
                'id': 'ps5-id',
                'name': 'PlayStation 5 Slim',
                'code': 'PS5-SLIM',
                'externalCode': 'external-id',
                'meta': {'type': 'product'},
                'salePrices': [{'value': 4999000, 'priceType': {'name': 'Розница'}}],
            }]
        }
        session = Mock()
        session.get.return_value = response

        assortment = MoySkladClient(session=session).list_assortment()

        self.assertEqual(assortment[0].name, 'PlayStation 5 Slim')
        self.assertEqual(str(assortment[0].prices[0][1]), '49990')
        self.assertEqual(session.get.call_args.kwargs['params'], {'limit': 1000, 'offset': 0})

    @override_settings(MOYSKLAD_ACCESS_TOKEN='test-token')
    def test_includes_safe_api_error_detail(self):
        response = Mock(status_code=400)
        response.json.return_value = {'errors': [{'error': 'Недопустимый параметр'}]}
        response.raise_for_status.side_effect = requests.HTTPError(response=response)
        session = Mock()
        session.get.return_value = response

        with self.assertRaisesMessage(MoySkladError, 'Недопустимый параметр'):
            MoySkladClient(session=session).list_warehouses()

    @override_settings(MOYSKLAD_ACCESS_TOKEN='test-token')
    def test_reads_free_stock_for_selected_warehouse(self):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            'rows': [{
                'meta': {'href': 'https://api.moysklad.ru/api/remap/1.2/entity/product/product-id'},
                'stockByStore': [
                    {'meta': {'href': 'https://api.moysklad.ru/api/remap/1.2/entity/store/other'}, 'stock': 9},
                    {'meta': {'href': 'https://api.moysklad.ru/api/remap/1.2/entity/store/store-id'}, 'stock': 3, 'reserve': 1},
                ],
            }],
        }
        session = Mock()
        session.get.return_value = response

        stock = MoySkladClient(session=session).list_stock_for_store('store-id')

        self.assertEqual(str(stock['product-id'].stock), '3')
        self.assertEqual(str(stock['product-id'].free_stock), '2')
        self.assertEqual(
            session.get.call_args.kwargs['params'],
            {'limit': 1000, 'offset': 0},
        )


class MoySkladMatchingTests(SimpleTestCase):
    def test_normalizes_common_console_vocabulary(self):
        tokens = normalized_tokens('PlayStation 5 Slim с дисководом, новая')
        self.assertTrue({'ps', '5', 'slim', 'disc', 'new'} <= tokens)

    def test_related_names_rank_above_unrelated_names(self):
        target = 'PlayStation 5 Slim с дисководом'
        self.assertGreater(
            score(target, 'PS5 SLIM DISC NEW ACT'),
            score(target, 'Кофемашина DeLonghi'),
        )
