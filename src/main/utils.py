import base64

from urllib.parse import urlencode

from hashlib import sha256
from dataclasses import dataclass

from decimal import Decimal
from django.db.models.query import Prefetch

from constance import config

from . import models

from rest_framework.exceptions import ValidationError


BASE_PAYEER_URL = 'https://payeer.com/merchant/?'


@dataclass
class PayeerData:
    order_id: int
    amount: float
    currency: str
    description: str


def _parse_items(item_map: dict, item: dict) -> None:
    item_map[item['uuid']] = item

    for child in item.get('children', []):
        _parse_items(item_map, child)


def _get_item_map(product: models.Product) -> dict:
    item_map = dict()

    for section in product.additional_options:
        for item in section.get('children', []):
            _parse_items(item_map, item)

    return item_map


def _get_price_for_oder_product(order_product: 'models.OrderProduct') -> Decimal:
    resulting_price: Decimal = order_product.product.price * order_product.amount

    selected_items = order_product.selected_items
    selected_items_meta = order_product.selected_items_meta

    if not selected_items:
        return resulting_price

    item_map = _get_item_map(order_product.product)

    if not item_map:
        # That's the odd behaviour if we passed the first condition but okay
        return resulting_price

    for item_uuid in selected_items:
        item = item_map[item_uuid]

        if item['item'] == 'number-input':
            meta = selected_items_meta[item_uuid]
            
            if meta:
                # TODO: Fix at FE
                step_size = int(item['meta']['step_size'])
                resulting_price += Decimal(item['price_modifier'] * (meta['value'] / step_size))

                continue

        resulting_price += Decimal(item['price_modifier'])

    return resulting_price


def get_order_price(order_id: int) -> Decimal:
    order = models.Order.objects.filter(
        id=order_id,
    ).prefetch_related(
        Prefetch(
            'order_products',
            models.OrderProduct.objects.select_related(
                'product',
            ),
        ),
    ).first()

    if not order:
        raise ValidationError('Order #%s is not found!' % order_id)

    resulting_price = Decimal(0)

    # TODO: Fix typings
    for order_product in order.order_products.all():
        resulting_price += _get_price_for_oder_product(order_product)

    return resulting_price


def get_payeer_url(data: PayeerData) -> str:
    key = config.PAYEER_KEY
    merchant_id = config.PAYEER_MERCHANT_ID

    description = base64.b64encode(data.description.encode('utf-8')).decode('utf-8')

    signature_values = (
        merchant_id,
        data.order_id,
        data.amount,
        data.currency,
        description,
        key,
    )
    
    signature_string = ':'.join([
        str(value)
        for value in signature_values
    ])

    signature = sha256(signature_string.encode('utf-8')).hexdigest().upper()

    return BASE_PAYEER_URL + urlencode({
        'm_shop': merchant_id,
        'm_orderid': data.order_id,
        'm_amount': data.amount,
        'm_curr': data.currency,
        'm_desc': description,
        'm_sign': signature,
    })


def set_default_currency(currency_id: int) -> None:
    models.Currency.objects.all().update(is_default=False)

    models.Currency.objects.filter(
        id=currency_id,
    ).update(is_default=True)
