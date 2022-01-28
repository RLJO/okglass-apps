# -*- coding: utf-8 -*-
{
    'name': 'Antsroute Delivery',
    'version': '13.0.1.0.0',
    'category': 'Inventory/Delivery',
    'description': """Antsroute delivery""",
    'author': 'ANSTROUTE, SimplicIT',
    'website': 'https://antsroute.com/',
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
    'installable': True,
    'application': True,
    #'external_dependencies': {
    #    'python': ['xmltodict'],
    #},
    #'license': '????',
}
