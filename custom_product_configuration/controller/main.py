from odoo.http import request
from werkzeug.exceptions import NotFound
from odoo.addons.auth_signup.controllers.main import AuthSignupHome as Home
from odoo.exceptions import UserError
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import fields, http, tools, _
import json
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

        backend_details = ''

        if kw.get('backend_details'):
            backend_details = json.loads(kw.get('backend_details'))

        sale_order._cart_update(
            product_id=int(product_id),
            add_qty=add_qty,
            set_qty=set_qty,
            backend_details=backend_details,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values
        )
        return request.redirect("/shop/cart")

