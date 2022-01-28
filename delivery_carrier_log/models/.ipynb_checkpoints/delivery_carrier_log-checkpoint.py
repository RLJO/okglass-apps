# -*- coding: utf-8 -*-

from odoo import models, fields, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import requests, json

import logging
_logger = logging.getLogger(__name__)


class DeliveryCarrierLog(models.Model):
    _name = 'delivery.carrier.log'
    _description = 'Delivery carrier log'
    _order = 'date_log desc'

    date_log = fields.Datetime("Date")
    carrier_id = fields.Many2one('delivery.carrier', string="Carrier")
    picking_id = fields.Many2one('stock.picking', string="Stock picking")
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user)

    log_type = fields.Selection([('error', 'Error'), ('info', 'Information'), ('warning', 'Warning'),], string='Type')
    name = fields.Char(string="Name")
    technical_info_1 = fields.Text(string="Technical information 1")
    technical_info_2 = fields.Text(string="Technical information 2")
    technical_info_3 = fields.Text(string="Technical information 3")
    technical_info_4 = fields.Text(string="Technical information 4")
