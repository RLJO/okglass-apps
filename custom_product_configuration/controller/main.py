from odoo.http import request
from werkzeug.exceptions import NotFound
from odoo.addons.auth_signup.controllers.main import AuthSignupHome as Home
from odoo.exceptions import UserError
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import fields, http, tools, _
import json
import base64

class WebsiteSale(WebsiteSale):

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        print("\n\n\n===========NEW======cart_update==========",kw)
        """This route is called when adding a product to cart (no options)."""
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)

        product_custom_attribute_values = None
        if kw.get('product_custom_attribute_values'):
            product_custom_attribute_values = json.loads(kw.get('product_custom_attribute_values'))

        no_variant_attribute_values = None
        if kw.get('no_variant_attribute_values'):
            no_variant_attribute_values = json.loads(kw.get('no_variant_attribute_values'))

        backend_details = format = special_size = kantenauswahl = ''
        top_left_ecken = top_right_ecken = bottom_right_ecken = bottom_left_ecken = ''
        sketch = sketch_name = ''
        width_input = width_input_1 = width_input_2 = height_input = height_input_1 =''

        fmt_data = json.loads(kw.get('form_data'))

        sketch_ids = ''
        if fmt_data.get('other_expenses_ids'):
            sketch_ids = []
            for job in fmt_data.get('other_expenses_ids'):
                sketch_ids.append((0, 0, job))

        if kw.get('backend_details'):
            backend_details = json.loads(kw.get('backend_details'))

        if kw.get('format'):
            format = kw.get('format')

        if kw.get('special_size'):
            special_size = kw.get('special_size')

        if kw.get('kantenauswahl'):
            kantenauswahl = kw.get('kantenauswahl')

        if kw.get('top_left_ecken'):
            top_left_ecken = kw.get('top_left_ecken')

        if kw.get('top_right_ecken'):
            top_right_ecken = kw.get('top_right_ecken')

        if kw.get('bottom_right_ecken'):
            bottom_right_ecken = kw.get('bottom_right_ecken')

        if kw.get('bottom_left_ecken'):
            bottom_left_ecken = kw.get('bottom_left_ecken')

        if kw.get('format_width_input'):
            width_input = kw.get('format_width_input')

        if kw.get('format_width_input_1'):
            width_input_1 = kw.get('format_width_input_1')

        if kw.get('format_width_input_2'):
            width_input_2 = kw.get('format_width_input_2')

        if kw.get('format_height_input'):
            height_input = kw.get('format_height_input')

        if kw.get('format_height_input_1'):
            height_input_1 = kw.get('format_height_input_1')

        if kw.get('sketch'):
            sketch = base64.b64encode(kw.get('sketch').read())
            sketch_name = kw.get('sketch').filename


        sale_order._cart_update(
            product_id=int(product_id),
            add_qty=add_qty,
            set_qty=set_qty,
            backend_details=backend_details,
            format=format,
            special_size=special_size,
            kantenauswahl=kantenauswahl,
            top_left_ecken=top_left_ecken,
            top_right_ecken=top_right_ecken,
            bottom_right_ecken=bottom_right_ecken,
            bottom_left_ecken=bottom_left_ecken,
            width_input=width_input,
            width_input_1=width_input_1,
            width_input_2=width_input_2,
            height_input=height_input,
            height_input_1=height_input_1,
            sketch=sketch,
            sketch_name=sketch_name,
            sketch_ids=sketch_ids,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values
        )
        return request.redirect("/shop/cart")

