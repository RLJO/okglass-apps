# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import datetime
import logging
_logger = logging.getLogger(__name__)


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    @api.onchange('carrier_id')
    def _onchange_carrier_id(self):
        # Check if delivey date is allowed
        if self.carrier_id.use_antsroute:
            date_auth = {}
            date_auth[0] = self.carrier_id.antsroute_delivery_monday
            date_auth[1] = self.carrier_id.antsroute_delivery_tuesday
            date_auth[2] = self.carrier_id.antsroute_delivery_wednesday
            date_auth[3] = self.carrier_id.antsroute_delivery_thrusday
            date_auth[4] = self.carrier_id.antsroute_delivery_friday
            date_auth[5] = self.carrier_id.antsroute_delivery_saturday
            date_auth[6] = self.carrier_id.antsroute_delivery_sunday
            
            if self.order_id.commitment_date:
                date_to_check = self.order_id.commitment_date
            elif self.order_id.expected_date:
                date_to_check = self.order_id.expected_date
            else:
                date_to_check = False
            
            if date_to_check and date_auth[date_to_check.weekday()] is False:
                raise UserError(_("The selected delivery day is not authorized for this carrier"))
                
        super(ChooseDeliveryCarrier, self)._onchange_carrier_id()
