# -*- coding: utf-8 -*-

from odoo import models, fields, _

import logging
_logger = logging.getLogger(__name__)


class ProviderAntsroute(models.Model):
    _inherit = 'delivery.carrier'

    use_carrier_shipping = fields.Boolean("Use carrier shipping", compute='_compute_use_carrier_shipping')
    
    def _compute_use_carrier_shipping(self):
        for carrier in self:
            carrier.use_carrier_shipping = False