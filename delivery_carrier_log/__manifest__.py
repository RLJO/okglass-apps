# -*- coding: utf-8 -*-
{
    'name': 'Delivery carrier logs',
    'version': '14.0.1.0.0',
    'category': 'Inventory/Delivery',
    'description': """Delivery carrier logs""",
    'author': 'ANSTROUTE, SimplicIT',
    'website': 'https://antsroute.com/',
    'depends': [
        'delivery',
        'delivery_carrier_shipping_state',
    ],
    'data': [
        'views/delivery_carrier_log.xml',
        'views/stock_picking.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'price': 0.0,
    'currency': 'EUR',
}
