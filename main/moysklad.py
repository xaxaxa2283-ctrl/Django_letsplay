"""Read-only client for the first phase of the MoySklad integration."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import requests
from django.conf import settings


class MoySkladError(RuntimeError):
    """A safe error suitable for the management command output."""


@dataclass(frozen=True)
class MoySkladWarehouse:
    id: str
    name: str


@dataclass(frozen=True)
class MoySkladAssortment:
    id: str
    name: str
    entity_type: str
    code: str
    external_code: str
    prices: tuple[tuple[str, Decimal], ...]


class MoySkladClient:
    """A deliberately read-only JSON API client.

    It contains no POST, PUT or DELETE methods. Creating customer orders is a
    later, separate rollout after stock synchronization has been verified.
    """

    def __init__(
        self,
        *,
        access_token: str | None = None,
        api_url: str | None = None,
        timeout: int | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self.access_token = (access_token if access_token is not None else settings.MOYSKLAD_ACCESS_TOKEN).strip()
        self.api_url = (api_url or settings.MOYSKLAD_API_URL).rstrip('/')
        self.timeout = timeout if timeout is not None else settings.MOYSKLAD_REQUEST_TIMEOUT
        self.session = session or requests.Session()

    def _get(self, path: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.access_token:
            raise MoySkladError('Не задана переменная окружения MOYSKLAD_ACCESS_TOKEN.')
        try:
            response = self.session.get(
                f'{self.api_url}/{path.lstrip("/")}',
                params=params,
                headers={
                    'Authorization': f'Bearer {self.access_token}',
                    # The MoySklad JSON API rejects plain application/json.
                    'Accept': 'application/json;charset=utf-8',
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.HTTPError as exc:
            # The API error body identifies configuration/permission problems.
            # It never contains the sent access token, and is more useful than
            # requests' URL-only exception when diagnosing a failed setup.
            response = exc.response
            detail = ''
            if response is not None:
                try:
                    payload = response.json()
                except ValueError:
                    payload = None
                if isinstance(payload, dict):
                    errors = payload.get('errors')
                    if isinstance(errors, list):
                        parts = []
                        for error in errors[:3]:
                            if isinstance(error, dict):
                                text = error.get('error') or error.get('message') or error.get('code')
                                if text:
                                    parts.append(str(text))
                        detail = '; '.join(parts)
                if not detail:
                    detail = str(getattr(response, 'text', '')).strip().replace('\n', ' ')[:500]
            suffix = f' Причина API: {detail}' if detail else ''
            raise MoySkladError(f'МойСклад вернул HTTP {getattr(response, "status_code", "ошибку")}.{suffix}') from exc
        except requests.RequestException as exc:
            raise MoySkladError(f'Не удалось прочитать данные МоегоСклада: {exc}') from exc
        try:
            data = response.json()
        except ValueError as exc:
            raise MoySkladError('МойСклад вернул ответ не в формате JSON.') from exc
        if not isinstance(data, dict):
            raise MoySkladError('МойСклад вернул неожиданный формат ответа.')
        return data

    def list_warehouses(self) -> list[MoySkladWarehouse]:
        """Return all warehouses, following the API collection pagination."""
        warehouses: list[MoySkladWarehouse] = []
        offset = 0
        limit = 100
        while True:
            data = self._get('entity/store', params={'limit': limit, 'offset': offset})
            rows = data.get('rows')
            if not isinstance(rows, list):
                raise MoySkladError('В ответе МоегоСклада отсутствует список складов.')
            for row in rows:
                if not isinstance(row, dict) or not row.get('id') or not row.get('name'):
                    continue
                warehouses.append(MoySkladWarehouse(id=str(row['id']), name=str(row['name'])))
            if len(rows) < limit:
                return warehouses
            offset += limit

    def list_assortment(self) -> list[MoySkladAssortment]:
        """Read the accounting catalogue without changing it or the site."""
        result: list[MoySkladAssortment] = []
        offset = 0
        limit = 1000
        while True:
            data = self._get('entity/assortment', params={'limit': limit, 'offset': offset})
            rows = data.get('rows')
            if not isinstance(rows, list):
                raise MoySkladError('В ответе МоегоСклада отсутствует список ассортимента.')
            for row in rows:
                if not isinstance(row, dict) or not row.get('id') or not row.get('name'):
                    continue
                meta = row.get('meta') if isinstance(row.get('meta'), dict) else {}
                prices: list[tuple[str, Decimal]] = []
                for sale_price in row.get('salePrices', []):
                    if not isinstance(sale_price, dict) or sale_price.get('value') is None:
                        continue
                    price_type = sale_price.get('priceType')
                    label = price_type.get('name') if isinstance(price_type, dict) else None
                    prices.append((str(label or 'Цена продажи'), Decimal(str(sale_price['value'])) / 100))
                result.append(MoySkladAssortment(
                    id=str(row['id']),
                    name=str(row['name']),
                    entity_type=str(meta.get('type') or ''),
                    code=str(row.get('code') or ''),
                    external_code=str(row.get('externalCode') or ''),
                    prices=tuple(prices),
                ))
            if len(rows) < limit:
                return result
            offset += limit
