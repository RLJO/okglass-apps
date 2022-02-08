from datetime import datetime


from odoo import fields, models, api, _
# from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"
    _description = "Sales Order"
    _order = 'name desc'

    purchase_order_id = fields.Many2one(comodel_name="purchase.order", string="PO#", copy=False)
    vendor_id = fields.Many2one(comodel_name='res.partner', string="Vendor")


    def action_confirm(self):
        """ inherited to create sale order,
         first check for an existing sale order for the corresponding SO
         if does not exist, create a new purchase order"""
        for record in self:
            res = super(SaleOrder, self).action_confirm()
            if not record.purchase_order_id and record.vendor_id:
                purchase_order_lines_obj = self.env['purchase.order.line']

                purchase_order_obj = self.env['purchase.order']


                vals = {
                    "partner_id": record.vendor_id.id,
                    "sale_order_id": record.id,
                    "customer_id": record.partner_id.id,
                    #"name": record.name,
                    "currency_id": record.currency_id.id,

                }
                purchase = purchase_order_obj.create(vals)
                print('---purchase--',purchase)
                record.purchase_order_id = purchase.id
                print('--purchasere---',record.purchase_order_id)
                for line in record.order_line:
                    taxes = line.product_id.supplier_taxes_id
                    fpos = record.fiscal_position_id
                    taxes_id = fpos.map_tax(taxes, line.product_id, record.vendor_id) if fpos else taxes
                    if taxes_id:
                        taxes_id = taxes_id.filtered(lambda x: x.company_id.id == record.company_id.id)

                    purchase_order_line = purchase_order_lines_obj.create({'product_id': line.product_id.id,
                                                                           'name': line.name,
                                                                           'product_qty': line.product_uom_qty,
                                                                           "date_planned": datetime.today(),
                                                                           "product_uom": line.product_uom.id,
                                                                           'price_unit': line.price_unit,
                                                                           "order_id": purchase.id,
                                                                           "sale_order_line_id": line.id,
                                                                           # "discount": line.discount,
                                                                           'taxes_id': [(6, 0, taxes_id.ids)],
                                                                           })
                    line.purchase_order_line_id = purchase_order_line.id

            return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    purchase_order_line_id = fields.Many2one("purchase.order.line", string='Purchase Order Line')