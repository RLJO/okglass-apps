# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import requests, json, logging
from odoo import http, _
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from odoo.exceptions import UserError
from odoo.addons.website.controllers.main import QueryURL
import base64


class Website(Website):

    @http.route('/', auth='public', website='True', type='http', csrf=False)
    def index(self, **kw):
        return request.render('ecommerce_custom.home_template', {})

