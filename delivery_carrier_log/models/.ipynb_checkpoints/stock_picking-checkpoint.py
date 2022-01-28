# -*- coding: utf-8 -*-f

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    delivery_carrier_log_ids = fields.One2many('delivery.carrier.log', 'picking_id', string='Logs')