###################################################################################
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import base64
from datetime import date, timedelta, datetime
from odoo.tools import float_is_zero, float_compare



class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    _description = "Purchase Order"
    _order = 'name desc'

    sale_order_id = fields.Many2one(comodel_name="sale.order", string="SO#", copy=False)
    customer_id = fields.Many2one(comodel_name='res.partner', string="Customer")



    def button_confirm(self):
        """ inherited to create sale order,
         first check for an existing sale order for the corresponding PO
         if does not exist, create a new sale order"""
        for record in self:
            res = super(PurchaseOrder, self).button_confirm()
            if not record.sale_order_id and record.customer_id:
                sale_order_line_obj = self.env['sale.order.line']

                sale_order_obj = self.env['sale.order']


                vals = {
                    "partner_id": record.customer_id.id,
                    "vendor_id": record.partner_id.id,
                    "purchase_order_id": record.id,

                   # "name": record.name,

                    "currency_id": record.currency_id.id,

                }
                sale_order = sale_order_obj.create(vals)
                record.sale_order_id = sale_order.id
                for line in record.order_line:
                    taxes = line.product_id.taxes_id
                    fpos = record.fiscal_position_id
                    taxes_id = fpos.map_tax(taxes, line.product_id, record.partner_id) if fpos else taxes
                    if taxes_id:
                        taxes_id = taxes_id.filtered(lambda x: x.company_id.id == record.company_id.id)
                    sale_order_line = sale_order_line_obj.create({'product_id': line.product_id.id,
                                                                  'name': line.name,
                                                                  'tax_id': [(6, 0, taxes_id.ids)],
                                                                  'product_uom_qty': line.product_qty,
                                                                  "product_uom": line.product_uom.id,
                                                                  'price_unit': line.price_unit,
                                                                  "order_id": sale_order.id,
                                                                  # "discount": line.discount,
                                                                  "purchase_order_line_id": line.id,
                                                                  #"actual_qty": line.actual_qty
                                                                  })
                    line.sale_order_line_id = sale_order_line.id

            return res

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    sale_order_line_id = fields.Many2one("sale.order.line", string='Sale Order Line')