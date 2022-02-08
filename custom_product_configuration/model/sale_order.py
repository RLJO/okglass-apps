import logging
from odoo import models, fields, api, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_date = fields.Date(string="Payment Date")
    partner_invoice_id_char = fields.Char("Invoice Address", compute='compute_partner_invoice_address')
    partner_shipping_id_char = fields.Char("Delivery Address", compute='compute_partner_shipping_address')
    sketch_name_char = fields.Char("Attachments", compute='compute_sketch_name_char')

    @api.depends('order_line','order_line.sketch_name')
    def compute_sketch_name_char(self):
        for rec in self:
            sketch_name_char = ""
            for line in rec.order_line:
                if line.sketch_name:
                    sketch_name_char += line.sketch_name + ' '
            rec.sketch_name_char = sketch_name_char

    @api.depends('partner_invoice_id')
    def compute_partner_invoice_address(self):
        for rec in self:

            cust_street = rec.partner_invoice_id.street
            cust_street2 = rec.partner_invoice_id.street2
            cust_city = rec.partner_invoice_id.city
            cust_state_id = rec.partner_invoice_id.state_id
            cust_zip = rec.partner_invoice_id.zip
            cust_country_id = rec.partner_invoice_id.country_id

            cust_address = ""
            if cust_street:
                cust_address += cust_address + ' '
            if cust_street2:
                cust_address += cust_street2 + ' '
            if cust_city:
                cust_address += cust_city + ' '
            if cust_state_id:
                cust_address += cust_state_id.name + ' '
            if cust_zip:
                cust_address += cust_zip + ' '
            if cust_country_id:
                cust_address += cust_country_id.name + ' '

            rec.partner_invoice_id_char = cust_address

    # geminatecs
    @api.depends('partner_shipping_id')
    def compute_partner_shipping_address(self):
        for rec in self:

            cust_street = rec.partner_shipping_id.street
            cust_street2 = rec.partner_shipping_id.street2
            cust_city = rec.partner_shipping_id.city
            cust_state_id = rec.partner_shipping_id.state_id
            cust_zip = rec.partner_shipping_id.zip
            cust_country_id = rec.partner_shipping_id.country_id

            cust_address = ""
            if cust_street:
                cust_address += cust_address + ' '
            if cust_street2:
                cust_address += cust_street2 + ' '
            if cust_city:
                cust_address += cust_city + ' '
            if cust_state_id:
                cust_address += cust_state_id.name + ' '
            if cust_zip:
                cust_address += cust_zip + ' '
            if cust_country_id:
                cust_address += cust_country_id.name + ' '

            rec.partner_shipping_id_char = cust_address

            # @api.multi
    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        print("\n\n\n========_cart_update========",kwargs)
        """ Add or set product quantity, add_qty can be negative """
        self.ensure_one()
        product_context = dict(self.env.context)
        product_context.setdefault('lang', self.sudo().partner_id.lang)
        SaleOrderLineSudo = self.env['sale.order.line'].sudo().with_context(product_context)

        try:
            if add_qty:
                add_qty = int(add_qty)
        except ValueError:
            add_qty = 1
        try:
            if set_qty:
                set_qty = int(set_qty)
        except ValueError:
            set_qty = 0
        quantity = 0
        order_line = False
        if self.state != 'draft':
            request.session['sale_order_id'] = None
            raise UserError(_('It is forbidden to modify a sales order which is not in draft status.'))
        if line_id is not False:
            order_line = self._cart_find_product_line(product_id, line_id, **kwargs)[:1]
        print("============order_line============", order_line)
        # Create line if no line with product_id can be located
        if not order_line:
            # change lang to get correct name of attributes/values
            product = self.env['product.product'].with_context(product_context).browse(int(product_id))
            print("============product============", product)

            if not product:
                raise UserError(_("The given product does not exist therefore it cannot be added to cart."))

            no_variant_attribute_values = kwargs.get('no_variant_attribute_values') or []
            received_no_variant_values = product.env['product.template.attribute.value'].browse(
                [int(ptav['value']) for ptav in no_variant_attribute_values])
            received_combination = product.product_template_attribute_value_ids | received_no_variant_values
            product_template = product.product_tmpl_id

            # handle all cases where incorrect or incomplete data are received
            combination = product_template._get_closest_possible_combination(received_combination)

            # get or create (if dynamic) the correct variant
            product = product_template._create_product_variant(combination)

            if not product:
                raise UserError(_("The given combination does not exist therefore it cannot be added to cart."))

            product_id = product.id

            values = self._website_product_id_change(self.id, product_id, qty=1)

            # add no_variant attributes that were not received
            for ptav in combination.filtered(
                    lambda ptav: ptav.attribute_id.create_variant == 'no_variant' and ptav not in received_no_variant_values):
                no_variant_attribute_values.append({
                    'value': ptav.id,
                    'attribute_name': ptav.attribute_id.name,
                    'attribute_value_name': ptav.name,
                })

            # save no_variant attributes values
            if no_variant_attribute_values:
                values['product_no_variant_attribute_value_ids'] = [
                    (6, 0, [int(attribute['value']) for attribute in no_variant_attribute_values])
                ]

            # add is_custom attribute values that were not received
            custom_values = kwargs.get('product_custom_attribute_values') or []
            received_custom_values = product.env['product.attribute.value'].browse(
                [int(ptav['attribute_value_id']) for ptav in custom_values])

            for ptav in combination.filtered(
                    lambda ptav: ptav.is_custom and ptav.product_attribute_value_id not in received_custom_values):
                custom_values.append({
                    'attribute_value_id': ptav.product_attribute_value_id.id,
                    'attribute_value_name': ptav.name,
                    'custom_value': '',
                })

            # save is_custom attributes values
            if custom_values:
                values['product_custom_attribute_value_ids'] = [(0, 0, {
                    'attribute_value_id': custom_value['attribute_value_id'],
                    'custom_value': custom_value['custom_value']
                }) for custom_value in custom_values]

            # create the line
            if kwargs.get('backend_details'):
                print("============FINEL PRICE==============",kwargs.get('price_unit'))
                values.update({
                    'backend_details': kwargs.get('backend_details') if kwargs.get('backend_details') else '',
                    'format': kwargs.get('format') if kwargs.get('format') else '',
                    'special_size': kwargs.get('special_size') if kwargs.get('special_size') else '',
                    'kantenauswahl': kwargs.get('kantenauswahl') if kwargs.get('kantenauswahl') else '',
                    'top_left_ecken': kwargs.get('top_left_ecken') if kwargs.get('top_left_ecken') else '',
                    'top_right_ecken': kwargs.get('top_right_ecken') if kwargs.get('top_right_ecken') else '',
                    'bottom_right_ecken': kwargs.get('bottom_right_ecken') if kwargs.get('bottom_right_ecken') else '',
                    'bottom_left_ecken': kwargs.get('bottom_left_ecken') if kwargs.get('bottom_left_ecken') else '',
                    'width_input': kwargs.get('width_input') if kwargs.get('width_input') else '',
                    'width_input_1': kwargs.get('width_input_1') if kwargs.get('width_input_1') else '',
                    'width_input_2': kwargs.get('width_input_2') if kwargs.get('width_input_2') else '',
                    'height_input': kwargs.get('height_input') if kwargs.get('height_input') else '',
                    'height_input_1': kwargs.get('height_input_1') if kwargs.get('height_input_1') else '',
                    # 'price_unit': int(kwargs.get('price_unit')) if kwargs.get('price_unit') else product.lst_price,
                    'sketch': kwargs.get('sketch') if kwargs.get('sketch') else '',
                    'sketch_name': kwargs.get('sketch_name') if kwargs.get('sketch_name') else '',
                    'sketch_ids': kwargs.get('sketch_ids') if kwargs.get('sketch_ids') else False,
                    'name': kwargs.get('backend_details') if kwargs.get('backend_details') else '',
                    # 'price_unit':800,
                })
            print("============values============", values)
            order_line = SaleOrderLineSudo.create(values)
            print("============order_line============",order_line.name,order_line.price_unit)
            # Generate the description with everything. This is done after
            # creating because the following related fields have to be set:
            # - product_no_variant_attribute_value_ids
            # - product_custom_attribute_value_ids
            order_line.name = order_line.get_sale_order_line_multiline_description_sale(product)

            try:
                order_line._compute_tax_id()
            except ValidationError as e:
                # The validation may occur in backend (eg: taxcloud) but should fail silently in frontend
                _logger.debug("ValidationError occurs during tax compute. %s" % (e))
            if add_qty:
                add_qty -= 1

        # compute new quantity
        if set_qty:
            quantity = set_qty
        elif add_qty is not None:
            quantity = order_line.product_uom_qty + (add_qty or 0)

        # Remove zero of negative lines
        if quantity <= 0:
            order_line.unlink()
        else:
            # update line
            no_variant_attributes_price_extra = [ptav.price_extra for ptav in
                                                 order_line.product_no_variant_attribute_value_ids]
            values = self.with_context(
                no_variant_attributes_price_extra=no_variant_attributes_price_extra)._website_product_id_change(self.id,
                                                                                                                product_id,
                                                                                                                qty=quantity)
            if self.pricelist_id.discount_policy == 'with_discount' and not self.env.context.get('fixed_price'):
                order = self.sudo().browse(self.id)
                product_context.update({
                    'partner': order.partner_id,
                    'quantity': quantity,
                    'date': order.date_order,
                    'pricelist': order.pricelist_id.id,
                    'force_company': order.company_id.id,
                })
            product = self.env['product.product'].with_context(product_context).browse(product_id)
            values['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
                order_line._get_display_price(product),
                order_line.product_id.taxes_id,
                order_line.tax_id,
                self.company_id
            )

            if kwargs.get('backend_details'):
                values.update({
                    'price_unit': int(kwargs.get('price_unit')) if kwargs.get('price_unit') else product.lst_price,
                    # 'price_unit': 300,
                })

            order_line.write(values)

            # link a product to the sales order
            if kwargs.get('linked_line_id'):
                linked_line = SaleOrderLineSudo.browse(kwargs['linked_line_id'])
                order_line.write({
                    'linked_line_id': linked_line.id,
                    'name': order_line.name + "\n" + _("Option for:") + ' ' + linked_line.product_id.display_name,
                })
                linked_line.write(
                    {"name": linked_line.name + "\n" + _("Option:") + ' ' + order_line.product_id.display_name})

        option_lines = self.order_line.filtered(lambda l: l.linked_line_id.id == order_line.id)
        for option_line_id in option_lines:
            self._cart_update(option_line_id.product_id.id, option_line_id.id, add_qty, set_qty, **kwargs)

        return {'line_id': order_line.id, 'quantity': quantity, 'option_ids': list(set(option_lines.ids))}




class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    backend_details = fields.Char(string="Description", required=False)
    format = fields.Selection([('rectangle','Rectangle'),('ellipse','Ellipse'),('triangle','Triangle'),
                               ('spec_rectangle','Spec Rectangle'),('parallelogram','Parallelogram'),('trapezium','Trapezium'),
                               ('cropped_rectangle', 'Cropped Rectangle'), ],string="Format", required=False)
    special_size = fields.Selection([('4', '4 mm'), ('5', '5 mm'), ('6', '6 mm'),
                               ('8', '8 mm'), ('10', '10 mm'),
                               ('12', '12 mm'),
                               ('15', '15 mm'), ], string="Special Size", required=False)
    kantenauswahl = fields.Selection([('gesaumt', 'Gesäumt'), ('geschliffen', 'Matt geschliffen'), ('poliert', 'Hochglanz poliert'),
                               ], string="Kantenauswahl", required=False)
    top_left_ecken = fields.Selection(
        [('option_1', 'Option 1'), ('option_2', 'Option 2'), ('option_3', 'Option 3'),
         ], string="Top Left Ecken", required=False)
    top_right_ecken = fields.Selection(
        [('option_1', 'Option 1'), ('option_2', 'Option 2'), ('option_3', 'Option 3'),
         ], string="Top Right Ecken", required=False)
    bottom_right_ecken = fields.Selection(
        [('option_1', 'Option 1'), ('option_2', 'Option 2'), ('option_3', 'Option 3'),
         ], string="Bottom Right Ecken", required=False)
    bottom_left_ecken = fields.Selection(
            [('option_1', 'Option 1'), ('option_2', 'Option 2'), ('option_3', 'Option 3'),
         ], string="Bottom Left Ecken", required=False)
    sketch = fields.Binary(string="Skizze hochladen")
    sketch_name = fields.Char(string="Sketch Name")
    sketch_ids = fields.One2many('sketch.sketch', 'sale_order_line_id', string="Bohrungen")

    width_input = fields.Char(string="Width (mm)")
    width_input_1 = fields.Char(string="Width 1 (mm)")
    width_input_2 = fields.Char(string="Width 2 (mm)")
    height_input = fields.Char(string="Height (mm)")
    height_input_1 = fields.Char(string="Height 1 (mm)")

    def get_sale_order_line_multiline_description_sale(self, product):
        description = super(SaleOrderLine, self).get_sale_order_line_multiline_description_sale(product)
        if self.format and self.special_size:
            description = ''
            if self.product_id:
                description = description + self.product_id.name + '\n'
            if self.format:
                description = description + 'Format : ' + self.format + '\n'
            if self.special_size:
                description = description + 'Thickness : ' + self.special_size + '\n'
            if self.width_input:
                description = description + 'Width (mm) : ' + self.width_input + '\n'
            if self.height_input:
                description = description + 'Height (mm) : ' + self.height_input + '\n'
            if self.kantenauswahl:
                description = description + 'Kantenauswahl : ' + dict(self._fields['kantenauswahl'].selection).get(self.kantenauswahl) + '\n'
            if self.top_left_ecken:
                description = description + 'Top Left : ' + dict(self._fields['top_left_ecken'].selection).get(self.top_left_ecken) + '\n'
            if self.top_right_ecken:
                description = description + 'Top Right : ' + dict(self._fields['top_right_ecken'].selection).get(self.top_right_ecken) + '\n'
            if self.bottom_right_ecken:
                description = description + 'Bottom Right : ' + dict(self._fields['bottom_right_ecken'].selection).get(self.bottom_right_ecken) + '\n'
            if self.bottom_left_ecken:
                description = description + 'Bottom Left : ' + dict(self._fields['bottom_left_ecken'].selection).get(self.bottom_left_ecken) + '\n'
        # if self.backend_details:
        #     self.backend_details = self.backend_details.replace(',', '\n')
        #     description += "\n" + self.backend_details
        print("===========get_sale_order_line_multiline_description_sale==========",description)
        return description

