# -*- coding: utf-8 -*-f

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    use_antsroute = fields.Boolean(related='carrier_id.use_antsroute', store=True)
    
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)
    antsroute_order_price = fields.Monetary("Order price", copy=False, compute='_compute_antsroute_order_price')
    antsroute_shipping_value = fields.Monetary("Shipping value", copy=False)
    
    antsroute_shipping_qty = fields.Float("Shipping quantity", copy=False, compute='_compute_shipping_qty')
    antsroute_product_description = fields.Char("Product description", copy=False, compute='_compute_product_description')
    antsroute_delivery_date = fields.Datetime("Delivery date", copy=False)
    antsroute_delivery_status = fields.Char("Delivery status", copy=False)
    antsroute_delivery_driver = fields.Char("Driver name", copy=False)
    antsroute_delivery_vehicle_plate = fields.Char("Vehicle plate", copy=False)
    antsroute_delivery_signature = fields.Image("Delivery signature", max_width=1920, max_height=1920)
    antsroute_nb_delivery_photo = fields.Integer("Delivery photo number", default=0)
    antsroute_delivery_comment = fields.Text("Delivery comment") 
    antsroute_delivery_barcodes = fields.Text("Delivery barcodes") 

    def _cron_antsroute_check_picking_state(self):
        pickings = self.env['stock.picking'].search([
                ('antsroute_delivery_status', 'not in', ('DONE', 'DELETED', 'CANCELED')),
                ('use_antsroute', '=', True)
        ])
        for pick in pickings:
            _logger.warning(pick.name)
            if pick.carrier_id.active:
                pick.antsroute_get_delivery_info()
            
    
    def _set_scheduled_date(self):
        for picking in self:
            # Check if delivey date is allowed
            if picking.state not in ('draft', 'done', 'cancel'):
                if picking.carrier_id.use_antsroute:
                    date_auth = {}
                    date_auth[0] = picking.carrier_id.antsroute_delivery_monday
                    date_auth[1] = picking.carrier_id.antsroute_delivery_tuesday
                    date_auth[2] = picking.carrier_id.antsroute_delivery_wednesday
                    date_auth[3] = picking.carrier_id.antsroute_delivery_thrusday
                    date_auth[4] = picking.carrier_id.antsroute_delivery_friday
                    date_auth[5] = picking.carrier_id.antsroute_delivery_saturday
                    date_auth[6] = picking.carrier_id.antsroute_delivery_sunday
                    if picking.scheduled_date:
                        _logger.warning(picking.scheduled_date)
                        _logger.warning(date_auth)
                        _logger.warning(picking.state)
                        if date_auth[picking.scheduled_date.weekday()] is False:
                            raise UserError(_("The selected delivery day is not authorized for this carrier"))
        super(StockPicking, self)._set_scheduled_date()
    
    def action_cancel(self):
        if self.use_antsroute:
            self.carrier_id.antsroute_delete_request(self)
            self.antsroute_get_delivery_info()
        return super(StockPicking, self).action_cancel()
    
    def write(self, vals):
        if 'carrier_id' in vals and vals['carrier_id']:
            # We are changing carrier so we delete (if needed the request made to Antsroute)
            if self.use_antsroute:
                self.carrier_id.antsroute_delete_request(self)
                self.antsroute_get_delivery_info()
    
        return super(StockPicking, self).write(vals)
    
    @api.depends('move_line_ids', 'move_line_ids.result_package_id', 'move_line_ids.product_uom_id', 'move_line_ids.qty_done')
    def _compute_shipping_qty(self):
        for picking in self:
            qty = 0.0
            for move_line in picking.move_line_ids:
                if move_line.product_id and not move_line.result_package_id:
                    qty += move_line.qty_done
            picking.antsroute_shipping_qty = qty
    
    @api.depends('move_line_ids', 'move_line_ids.result_package_id', 'move_line_ids.product_uom_id', 'move_line_ids.qty_done')
    def _compute_product_description(self):
        for picking in self:
            description = ""
            for move_line in picking.move_line_ids:
                if move_line.product_id and not move_line.result_package_id and move_line.qty_done > 0:
                    description = description + ' ' + str(move_line.product_id.default_code) if move_line.product_id.default_code else str(move_line.product_id.name)
            picking.antsroute_product_description = description

    def _compute_antsroute_order_price(self):
        for picking in self:
            picking.currency_id = False
            picking.antsroute_order_price = False
            if picking.origin:
                order = self.env['sale.order'].search([('name', '=', picking.origin)])
                if order:
                    picking.currency_id = order.currency_id
                    picking.antsroute_order_price = order.amount_total
                    if picking.antsroute_shipping_value == False or picking.antsroute_shipping_value == 0:
                        picking.antsroute_shipping_value = picking.antsroute_order_price

    @api.depends('move_line_ids_without_package', 'sent_to_carrier', 'state')
    def _compute_antsroute_shipping_state(self):
        for picking in self:
            if picking.state == 'assigned' and picking.carrier_id and picking.carrier_id.use_antsroute:
                if picking.sent_to_carrier:
                    picking.antsroute_shipping_state = 'pickup_requested'
                else:
                    picking.antsroute_shipping_state = 'pickup_request'
            else:
                picking.antsroute_shipping_state = picking.state

    def send_to_carrier_for_pickup(self):
        self.ensure_one()
        
        if not self.carrier_id:
            raise UserError(_('Please define a carrier for this order first.'))
        
        if (self.carrier_id and self.state == "assigned"):
            # Lancement export ANTSROUTE
            if self.carrier_id.use_antsroute:
                self.carrier_id.antsroute_send_request(self)
                self.antsroute_get_delivery_info()
            else:
                raise UserError(_('No API to call for this carrier.'))
    
    def antsroute_get_delivery_info(self):
        self.ensure_one()
        
        if not self.carrier_id:
            raise UserError(_('Please define a carrier for this order first.'))
            
        if (self.carrier_id and self.state == "assigned"):
            # If carrier if Antsroute gather shipping information
            if self.carrier_id.use_antsroute:
                vals = self.carrier_id.antsroute_get_request_info(self)
                if vals:
                    self.update(vals)
            else:
                raise UserError(_('No API to call for this carrier.'))
    
