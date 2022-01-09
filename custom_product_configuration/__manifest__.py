# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': "Custom Product Configuration",

    'summary': "Custom Product Configuration",
    'author': "Bansi Patel",
    'website': "",
    'category': 'website',
    'version': '12.0.1.0.2',

    'depends': [
        'website_sale', 
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/product_details.xml',
        'views/product_template_view.xml',
    ],
    'installable': True,
}
