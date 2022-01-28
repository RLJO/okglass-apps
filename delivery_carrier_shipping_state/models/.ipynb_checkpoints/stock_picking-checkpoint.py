# -*- coding: utf-8 -*-f

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    sent_to_carrier = fields.Datetime("Sent to carrier", copy=False)
    use_carrier_shipping = fields.Boolean("Use carrier shipping", related='carrier_id.use_carrier_shipping')
    shipping_state = fields.Selection(string="Shipping state", 
        selection=[
            ('pickup_request', 'Pickup to request'),
            ('pickup_requested', 'Pickup requested'),
        ], compute='_compute_shipping_state', store=True, tracking=True)

    @api.depends('move_line_ids_without_package', 'sent_to_carrier', 'state', 'carrier_id')
    def _compute_shipping_state(self):
        for picking in self:
            if picking.state == 'assigned' and picking.carrier_id and picking.use_carrier_shipping:
                if picking.sent_to_carrier:
                    picking.shipping_state = 'pickup_requested'
                else:
                    picking.shipping_state = 'pickup_request'
            else:
                picking.shipping_state = False