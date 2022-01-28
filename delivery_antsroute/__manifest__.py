# -*- coding: utf-8 -*-
{
    'name': 'Odoo AntsRoute Delivery Connector',
    'version': '14.0.1.0.0',
    'category': 'Inventory/Delivery',
    'description': """Odoo AntsRoute Delivery Connector""",
    'summary': """'Odoo AntsRoute Delivery Connector helps you to transfer your delivery orders from Odoo to the route optimization and tracking software AntsRoute.""",
    'author': 'AntsRoute',
    'company': 'AntsRoute',
    'website': "https://antsroute.com/",
    'depends': [
        'delivery',
        'mail',
        'delivery_carrier_log',
        'delivery_carrier_shipping_state',
    ],
    'data': [
        'data/delivery_antsroute_data.xml',
        'views/delivery_carrier.xml',
        'views/stock_warehouse.xml',
        'views/stock_picking.xml'
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'price': 0.0,
    'currency': 'EUR',
}
