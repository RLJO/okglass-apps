import logging
from odoo import models, fields, api, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'


    description_1 = fields.Html("Description 1")
    description_2 = fields.Html("Description 2")
    size_table_ids = fields.One2many('size.size', 'size_table_id', string="Size Table")
    variant_detail_ids = fields.One2many('variant.details', 'variant_detail_id', string="Variant Detail Table")
    glass_ids = fields.One2many('glass.glass', 'product_id', string="Thickness Price Details")

    is_rectangle_bool = fields.Boolean('Active Rectangle')
    is_rectangle_img = fields.Binary('Rectangle Image')

    is_ellipse_bool = fields.Boolean('Active Ellipse')
    is_ellipse_img = fields.Binary('Ellipse Image')

    is_triangle_bool = fields.Boolean('Active Triangle')
    is_triangle_img = fields.Binary('Triangle Image')

    is_spec_rectangle_bool = fields.Boolean('Active Spec Rectangle')
    is_spec_rectangle_img = fields.Binary('Spec Rectangle Image')

    is_parallelogram_bool = fields.Boolean('Active Parallelogram')
    is_parallelogram_img = fields.Binary('Parallelogram Image')

    is_trapezium_bool = fields.Boolean('Active Trapezium')
    is_trapezium_img = fields.Binary('Trapezium Image')

    is_cropped_rectangle_bool = fields.Boolean('Active Cropped Rectangle')
    is_cropped_rectangle_img = fields.Binary('Cropped Rectangle Image')


class SketchSketch(models.Model):
    _name = 'sketch.sketch'

    num_1 = fields.Char("Durchmesser (mm)")
    num_2 = fields.Char("Abstand von links (mm)")
    num_3 = fields.Char("Abstand von oben (mm)")
    sale_order_line_id = fields.Many2one('sale.order.line')


class SizeSize(models.Model):
    _name = 'size.size'

    size_table_id = fields.Many2one('product.template')
    title = fields.Char("Title")
    description = fields.Char("Description")


class VariantDetails(models.Model):
    _name = 'variant.details'

    variant_detail_id = fields.Many2one('product.template')
    title = fields.Char("Title")
    description = fields.Char("Description")


class GlassGlass(models.Model):
    _name = 'glass.glass'

    product_id = fields.Many2one('product.template')
    thickness = fields.Char("Name")
    thickness_size = fields.Integer("Thickness (mm)")
    price = fields.Float("Price")




