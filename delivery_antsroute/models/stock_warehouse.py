# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.tools import float_repr


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'
    
    antsroute_warehouse_open = fields.Float(string='Warehouse default opening', default=4)
    antsroute_warehouse_close = fields.Float(string='Warehouse default closing', default=19)