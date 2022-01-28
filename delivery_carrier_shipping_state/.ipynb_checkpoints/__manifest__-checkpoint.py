# -*- coding: utf-8 -*-
{
    'name': 'Delivery carrier shipping state',
    'version': '13.0.1.0.0',
    'category': 'Inventory/Delivery',
    'description': """Delivery carrier shipping state""",
    'author': 'ANSTROUTE, SimplicIT',
    'website': 'https://antsroute.com/',
    'depends': [
        'delivery',
    ],
    'data': [
        'views/delivery_carrier.xml',
        'views/stock_picking.xml',
        #'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    #'external_dependencies': {
    #    'python': ['xmltodict'],
    #},
    #'license': '????',
}
