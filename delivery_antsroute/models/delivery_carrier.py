# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import math
import requests, json
import base64

import logging
_logger = logging.getLogger(__name__)


class ProviderAntsroute(models.Model):
    _inherit = 'delivery.carrier'

    use_antsroute = fields.Boolean(string='Use Antsroute',)
    antsroute_api_key = fields.Char(string='Antsroute API Key')
    antsroute_type = fields.Selection([('delivery', 'Pick-up delivery activated'),('service', 'Pick-up delivery not activated'),], string='Antsroute Mode', default='delivery')
    antsroute_destination = fields.Selection([('in_bucket', 'In the bucket'),('in_organise', 'In organize'),], string='Order destination in Antsroute', default='in_bucket')
    antsroute_average_loading_time = fields.Integer('Average loading time in minutes', default=10)
    antsroute_average_customer_unloading_time = fields.Integer('Average customer unloading time in minutes', default=10)
    
    antsroute_delivery_monday = fields.Boolean(string='Monday', default=True)
    antsroute_delivery_tuesday = fields.Boolean(string='Tuesday', default=True)
    antsroute_delivery_wednesday = fields.Boolean(string='Wednesday', default=True)
    antsroute_delivery_thrusday = fields.Boolean(string='Thursday', default=True)
    antsroute_delivery_friday = fields.Boolean(string='Friday', default=True)
    antsroute_delivery_saturday = fields.Boolean(string='Saturday', default=True)
    antsroute_delivery_sunday = fields.Boolean(string='Sunday', default=True)
    
    antsroute_warehouse_open = fields.Float(string='Warehouse default opening', default=4)
    antsroute_warehouse_close = fields.Float(string='Warehouse default closing', default=19)
    antsroute_customer_delivery_open = fields.Float(string='Customer default delivery start', default=4)
    antsroute_customer_delivery_close = fields.Float(string='Customer default delivery end', default=19)

    @api.depends('use_antsroute')
    def _compute_use_carrier_shipping(self):
        super(ProviderAntsroute, self)._compute_use_carrier_shipping()
        for carrier in self:
            if carrier.use_antsroute:
                carrier.use_carrier_shipping = True    
    
    def anstroute_get_external_id(self, picking):
        for carrier in self:
            # Compute order external id (stock.picking.id + sent_to_carrier)
            for pick in picking:
                order_external_id = False
                if pick.sent_to_carrier and carrier.use_antsroute:
                    order_external_id = "%s-%s" % (pick.id, pick.sent_to_carrier.strftime("%y%m%d%H%M%S"))
                return order_external_id
    
    def antsroute_send_request_prepare_data(self, picking, send_datetime):
        vals = {}
        for carrier in self:
            for pick in picking:
                # Préparation des données pour alimenter le WS
                hours, seconds = divmod(carrier.antsroute_customer_delivery_open * 60, 3600)  # split to hours and seconds
                minutes, seconds = divmod(seconds, 60)  # split the seconds to minutes and seconds
                customer_start = "{:02.0f}:{:02.0f}".format(minutes, seconds)
                hours, seconds = divmod(carrier.antsroute_customer_delivery_close * 60, 3600)  # split to hours and seconds
                minutes, seconds = divmod(seconds, 60)  # split the seconds to minutes and seconds
                customer_close = "{:02.0f}:{:02.0f}".format(minutes, seconds)               

                # Récupération des données de l'entrepot
                if pick.picking_type_id and pick.picking_type_id.warehouse_id:
                    if pick.picking_type_id.warehouse_id.antsroute_warehouse_open and pick.picking_type_id.warehouse_id.antsroute_warehouse_close:
                        hours, seconds = divmod(pick.picking_type_id.warehouse_id.antsroute_warehouse_open * 60, 3600)  # split to hours and seconds
                        minutes, seconds = divmod(seconds, 60)  # split the seconds to minutes and seconds
                        warehouse_start = "{:02.0f}:{:02.0f}".format(minutes, seconds)
                        hours, seconds = divmod(pick.picking_type_id.warehouse_id.antsroute_warehouse_close * 60, 3600)  # split to hours and seconds
                        minutes, seconds = divmod(seconds, 60)  # split the seconds to minutes and seconds
                        warehouse_close = "{:02.0f}:{:02.0f}".format(minutes, seconds) 
                    else:
                        hours, seconds = divmod(carrier.antsroute_warehouse_open * 60, 3600)  # split to hours and seconds
                        minutes, seconds = divmod(seconds, 60)  # split the seconds to minutes and seconds
                        warehouse_start = "{:02.0f}:{:02.0f}".format(minutes, seconds)
                        hours, seconds = divmod(carrier.antsroute_warehouse_close * 60, 3600)  # split to hours and seconds
                        minutes, seconds = divmod(seconds, 60)  # split the seconds to minutes and seconds
                        warehouse_close = "{:02.0f}:{:02.0f}".format(minutes, seconds)
                    warehouse_address = ""
                    if pick.picking_type_id.warehouse_id.partner_id:
                        if pick.picking_type_id.warehouse_id.partner_id.street:
                            warehouse_address = pick.picking_type_id.warehouse_id.partner_id.street
                        if pick.picking_type_id.warehouse_id.partner_id.street2:
                            warehouse_address = warehouse_address + ' ' + pick.picking_type_id.warehouse_id.partner_id.street2
                        if pick.picking_type_id.warehouse_id.partner_id.zip:
                            warehouse_address = warehouse_address + ' ' + pick.picking_type_id.warehouse_id.partner_id.zip
                        if pick.picking_type_id.warehouse_id.partner_id.city:
                            warehouse_address = warehouse_address + ' ' + pick.picking_type_id.warehouse_id.partner_id.city
                        if pick.picking_type_id.warehouse_id.partner_id.country_id:
                            warehouse_address = warehouse_address + ' ' + pick.picking_type_id.warehouse_id.partner_id.country_id.name
                    if warehouse_address == "":
                        raise UserError(_('API Antsroute : The warehouse has no address please add one.'))

                # Récupération de l'adresse du client
                if pick.partner_id:
                    customer_address = ""
                    if pick.partner_id:
                        if pick.partner_id.street:
                            customer_address = pick.partner_id.street
                        if pick.partner_id.street2:
                            customer_address = customer_address + ' ' + pick.partner_id.street2
                        if pick.partner_id.zip:
                            customer_address = customer_address + ' ' + pick.partner_id.zip
                        if pick.partner_id.city:
                            customer_address = customer_address + ' ' + pick.partner_id.city
                        if pick.partner_id.country_id:
                            customer_address = customer_address + ' ' + pick.partner_id.country_id.name
                    if customer_address == "":
                        raise UserError(_('API Antsroute : The customer has no address please add one.'))

                    # Préparation du commentaire chargement
                    loading_comment = ""
                    if pick.partner_id:
                        if pick.partner_id.name: 
                            loading_comment = pick.partner_id.name
                        else:
                            if pick.partner_id.parent_id and pick.partner_id.parent_id.name:
                                loading_comment = pick.partner_id.parent_id.name
                                
                    if loading_comment == False:
                        raise UserError(_('API Antsroute : The customer must have a name.'))
                    loading_comment = loading_comment + ' ' + pick.origin + ' ' + pick.name
                    if pick.note:
                        loading_comment = loading_comment + ' ' + pick.note
                    
                    # Préparation numéro de téléphone
                    phone_number = ''
                    if pick.partner_id.phone:
                        if pick.partner_id.mobile and pick.partner_id.mobile[0] == '+':
                            phone_number = pick.partner_id.phone
                        else:
                            if pick.partner_id.mobile:
                                phone_number = pick.partner_id.mobile
                            else:
                                phone_number = pick.partner_id.phone
                                
                    # Préparation mobile
                    mobile_number = ''
                    if pick.partner_id.mobile and pick.partner_id.mobile[0] == '+':
                        mobile_number = pick.partner_id.mobile

                    vals = {
                        "dueDate": pick.scheduled_date.strftime("%Y-%m-%d"),
                        "type": "DELIVERY" if carrier.antsroute_type == 'delivery' else "SERVICE",
                        "duration": carrier.antsroute_average_customer_unloading_time,
                        "externalId": str(pick.id) + "-" + send_datetime.strftime("%y%m%d%H%M%S"),
                        "comments": "",
                        "timeSlot": {
                            "start": customer_start,
                            "end": customer_close
                        },
                        "customer": {
                            "lastName": pick.partner_id.name,
                            "firstName": pick.partner_id.name,
                            "address": customer_address,
                            "phoneNumber": phone_number,
                            "mobileNumber": mobile_number,
                            "email": pick.partner_id.email or '',
                            "externalId": pick.partner_id.id,
                        },
                        "mandatoryAgent": "",
                        "customFields": [
                            {
                                "name": "Price",
                                "value": pick.antsroute_shipping_value
                            },
                            {
                                "name": "Description",
                                "value": pick.antsroute_product_description
                            },
                            {
                                "name": "Reference",
                                "value": pick.origin + ' ' + pick.name
                            }
                        ],
                        "capacities": [
                            {
                              "capacityName": "Weight",
                              "capacityValue": math.ceil(pick.shipping_weight)
                            },
                            {
                                "capacityName":"Number",
                                "capacityValue":pick.antsroute_shipping_qty
                            }
                        ],
                        "scheduleDate": pick.scheduled_date.strftime("%Y-%m-%d"),
                    }
                    if carrier.antsroute_type == 'delivery':
                        vals.update({
                            "loading": {
                                "location": {
                                  "name": pick.picking_type_id.warehouse_id.name,
                                  "address": warehouse_address
                                },
                                "duration": carrier.antsroute_average_loading_time,
                                "timeSlot": {
                                  "start": warehouse_start,
                                  "end": warehouse_close
                                },
                                "comments": loading_comment
                            },
                            "unloading": {
                                "location": {
                                  "name": pick.partner_id.name,
                                  "address": customer_address
                                },
                                "duration": carrier.antsroute_average_customer_unloading_time,
                                "timeSlot": {
                                  "start": customer_start,
                                  "end": customer_close
                                },
                                "comments": pick.note or ''
                            }
                        })
        return vals
    
    def antsroute_check_resquest_exist(self, picking):
        for carrier in self:
            vals_log = {}
            url_base = "https://app.antsroute.com"
            if self.antsroute_api_key:
                api_key = self.antsroute_api_key
            else:
                raise UserError(_('API Antsroute : No API Key defined on delivery carrier %s.' % carrier.name))
            
            # Compute order external id (stock.picking.id + sent_to_carrier)
            order_external_id = carrier.anstroute_get_external_id(picking)
            
            # Now we proceed checking if the pickup is in Antsroute system
            headers = {'Accept': 'application/json', 'cakey':api_key}
            url = "%s/capi/order/external-id/%s" % (url_base, order_external_id)
            response = requests.get(url, headers=headers)
            
            # Update of val_logs for logging
            vals_log.update({
                'carrier_id': carrier.id,
                'picking_id': picking.id,
                'technical_info_1': headers,
                'technical_info_2': url,
            })
            if response.status_code == 200:
                object_antsroute = json.loads(response.text)
                vals_log.update({
                    'date_log': datetime.now(),
                    'log_type': 'info',
                    'name': _("API Antsroute : Check if request exists : Pickup request exists"),
                    'technical_info_4': response.text,
                })
                delivery_log = self.env['delivery.carrier.log'].create(vals_log)
                return object_antsroute
            else:
                if response.status_code == 404:
                    vals_log.update({
                        'date_log': datetime.now(),
                        'log_type': 'warning',
                        'name': _("API Antsroute : Check if request exists : Pickup request does not exist"),
                    })
                    delivery_log = self.env['delivery.carrier.log'].create(vals_log)
                    return False
                else:
                    object_antsroute = json.loads(response.text)
                    if object_antsroute:
                        if object_antsroute and 'status' in object_antsroute and object_antsroute['status']:
                            # Error in API we log the details and tell the user
                            vals_log.update({
                                'date_log': datetime.now(),
                                'log_type': 'error',
                                'name': _("API Antsroute : Check if request exists : ERROR [%s] %s") % (object_antsroute['status'], object_antsroute['error']),
                            })
                            delivery_log = self.env['delivery.carrier.log'].create(vals_log)
                        else:
                            vals_log.update({
                                'date_log': datetime.now(),
                                'log_type': 'error',
                                'name': _("API Antsroute : Check if request exists : Unexpected error"),
                            })
                            delivery_log = self.env['delivery.carrier.log'].create(vals_log)
        return False
    
    def antsroute_delete_request(self, picking):
        for carrier in self:
            vals_log = {}
            
            url_base = "https://app.antsroute.com"
            if self.antsroute_api_key:
                api_key = self.antsroute_api_key
            else:
                raise UserError(_('API Antsroute : No API Key defined on delivery carrier %s.' % carrier.name))
            
            # Compute order external id (stock.picking.id + sent_to_carrier)
            order_external_id = carrier.anstroute_get_external_id(picking)
            
            # Now we proceed checking if the pickup is in Antsroute system
            headers = {'Accept': 'application/json', 'cakey':api_key}
            url = "%s/capi/order/external-id/%s" % (url_base, order_external_id)
            response = requests.delete(url, headers=headers)
            
            # Update of val_logs for logging
            vals_log.update({
                'carrier_id': carrier.id,
                'picking_id': picking.id,
                'technical_info_1': headers,
                'technical_info_2': url,
            })
            
            if response.status_code == 200:
                vals_log.update({
                    'date_log': datetime.now(),
                    'log_type': 'info',
                    'name': _("API Antsroute : Delete request : Pickup deleted with success"),
                })
                delivery_log = self.env['delivery.carrier.log'].create(vals_log)
                _logger.warning(vals_log)
                return 'proceed'
            else:
                if response.status_code == 404:
                    vals_log.update({
                        'date_log': datetime.now(),
                        'log_type': 'warning',
                        'name': _("API Antsroute : Delete request : Pickup not deleted (pickup not found in Antsroute)"),
                    })
                    delivery_log = self.env['delivery.carrier.log'].create(vals_log)
                    _logger.warning(vals_log)
                    return 'proceed'
                else:
                    object_antsroute = json.loads(response.text)
                    if object_antsroute:
                        if object_antsroute and 'status' in object_antsroute and object_antsroute['status']:
                            # Error in API we log the details and tell the user
                            vals_log.update({
                                'date_log': datetime.now(),
                                'log_type': 'error',
                                'name': _("API Antsroute : Delete request : ERROR [%s] %s") % (object_antsroute['status'], object_antsroute['error']),
                            })
                            delivery_log = self.env['delivery.carrier.log'].create(vals_log)
                            _logger.warning(vals_log)
                        elif object_antsroute and 'errorCode' in object_antsroute and object_antsroute['errorCode'] and 'message' in object_antsroute and object_antsroute['message']:
                            vals_log.update({
                                'date_log':datetime.now(),
                                'log_type':'error',
                                'name':_("API Antsroute : Delete request : ERROR [%s][%s] %s") % (response.status_code, object_antsroute['errorCode'], object_antsroute['message']),
                            })
                            delivery_log = self.env['delivery.carrier.log'].create(vals_log)
                            _logger.warning(vals_log)
                        else:
                            _logger.warning(object_antsroute)
                            vals_log.update({
                                'date_log': datetime.now(),
                                'log_type': 'error',
                                'name': _("API Antsroute : Delete request : Unexpected error"),
                            })
                            delivery_log = self.env['delivery.carrier.log'].create(vals_log)
                            _logger.warning(vals_log)
                        return delivery_log['name']
                    else:
                        return 'error'
    
    def antsroute_get_request_info(self, picking):
        vals = {}
        for carrier in self:
            vals_log = {}
            if picking:
                pick_info = carrier.antsroute_check_resquest_exist(picking)
                if pick_info:
                    # Data extraction to update delivery informations on the picking
                    vals = {}
                    if 'scheduledDate' in pick_info and pick_info['scheduledDate'] and 'estimatedTimeOfArrival' in pick_info and pick_info['estimatedTimeOfArrival']:
                        vals.update({'antsroute_delivery_date': pick_info['scheduledDate'] +' '+ pick_info['estimatedTimeOfArrival']})
                    else:
                        vals.update({'antsroute_delivery_date': ''})
                    if 'state' in pick_info and pick_info['state']:
                        vals.update({'antsroute_delivery_status': pick_info['state']})
                        if pick_info['state'] == 'DELETED' or pick_info['state'] == 'CANCELED':
                            picking.sent_to_carrier = False
                    else:
                        vals.update({'antsroute_delivery_status': ''})
                    if 'affectedAgent' in pick_info and pick_info['affectedAgent']:
                        vals.update({'antsroute_delivery_driver': pick_info['affectedAgent']})
                    else:
                        vals.update({'antsroute_delivery_driver': ''})
                    if 'resolutionComments' in pick_info and pick_info['resolutionComments']:
                        vals.update({'antsroute_delivery_comment': pick_info['resolutionComments']})
                    else:
                        vals.update({'antsroute_delivery_comment': ''})
                    if 'affectedVehicle' in pick_info and pick_info['affectedVehicle']:
                        vals.update({'antsroute_delivery_vehicle_plate': pick_info['affectedVehicle']})
                    else:
                        vals.update({'antsroute_delivery_vehicle_plate': ''})                    
                    if 'signature' in pick_info and pick_info['signature']:
                        img = carrier.anstroute_get_image(pick_info['signature'])
                        if img:
                            vals.update({'antsroute_delivery_signature': img})
                        else:
                            vals.update({'antsroute_delivery_signature': False})
                    else:
                        vals.update({'antsroute_delivery_signature': False})
                    
                    barcodes_value = ""
                    if 'barcodes' in pick_info and pick_info['barcodes']:
                        for barcode in pick_info['barcodes']:
                            if barcodes_value == '':
                                barcodes_value = "Code : " + str(barcode['value']) + " Quantité : " + str(barcode['quantity'])
                            else:
                                barcodes_value = barcodes_value + "\nCode : " + str(barcode['value']) + " Quantité : " + str(barcode['quantity'])
                    vals.update({'antsroute_delivery_barcodes': barcodes_value})
                    
                    nb_photos = picking.antsroute_nb_delivery_photo
                    if 'photos' in pick_info and pick_info['photos']:
                        for photo in pick_info['photos']:
                            img = carrier.anstroute_get_image(photo)
                            
                            if photo.split("/")[6] and photo.split("/")[8]:
                                name_photo = photo.split("/")[6] + "_" + photo.split("/")[8]
                            else:
                                name_photo = photo
                            img_exist = self.env['ir.attachment'].search([('name', '=', name_photo)])
                            if img_exist:
                                donothing = True
                            else:
                                nb_photos = nb_photos + 1
                                self.env['ir.attachment'].create({
                                    'name': name_photo,
                                    'datas': img,
                                    'res_model': 'stock.picking',
                                    'res_id': picking.id, 
                                })
                        picking.antsroute_nb_delivery_photo = nb_photos
                else:
                    vals.update({
                        'antsroute_delivery_date': '',
                        'antsroute_delivery_status': '',
                        'antsroute_delivery_driver': '',
                        'antsroute_delivery_comment': '',
                        'antsroute_delivery_signature': False,
                    })
                    picking.sent_to_carrier = False
        return vals
    
    def anstroute_get_image(self, url):
        for carrier in self:
            url_base = "https://app.antsroute.com"
            if self.antsroute_api_key:
                api_key = self.antsroute_api_key
            else:
                raise UserError(_('API Antsroute : No API Key defined on delivery carrier %s.' % carrier.name))
            
            headers = {'Accept': 'image/jpeg', 'cakey':api_key}
            response = requests.get(url, headers=headers)
            if response.content:
                object_antsroute = base64.encodestring(response.content).decode('ascii')
            else:
                object_antsroute = False
            return object_antsroute
            
    def antsroute_send_request(self, pickings):
        for carrier in self:
            vals_log = {}
                
            url_base = "https://app.antsroute.com"
            if self.antsroute_api_key:
                api_key = self.antsroute_api_key
            else:
                raise UserError(_('API Antsroute : Pickup Request : No API Key defined on delivery carrier %s.' % carrier.name))
            if self.antsroute_destination:
                if self.antsroute_destination == 'in_bucket':
                    end_point = "capi/order/basket"
                if self.antsroute_destination == 'in_organise':
                    end_point = "capi/order/planning"
            else:
                raise UserError(_('API Antsroute : Pickup Request : No destination defined on delivery carrier %s.' % carrier.name))
            
            headers = {'Content-type': 'application/json', 'Accept': 'application/json', 'cakey':api_key}
            url = "%s/%s" % (url_base, end_point)
            
            for pick in pickings:
                # We start with the data preparation for the antsroute webservice
                send_datetime = datetime.now()
                vals = carrier.antsroute_send_request_prepare_data(pick, send_datetime)
                
                # We check if the pickup was already requested
                # If so pickup order is deleted in Antsroute then recreated with new info as we cant update existing pickup via webservices
                delete = 'proceed'
                exist = carrier.antsroute_check_resquest_exist(pick)
                if exist:
                    # We delete the pickuprequest
                    delete = carrier.antsroute_delete_request(pick)
                
                if delete == 'proceed':
                    vals = json.dumps(vals)
                    response = requests.post(url, data=vals, headers=headers)

                    # Update of val_logs for logging
                    vals_log.update({
                        'carrier_id': carrier.id,
                        'picking_id': pick.id,
                        'technical_info_1':headers,
                        'technical_info_2':url,
                        'technical_info_3':vals,
                    })

                    if response.status_code == 201:
                        object_antsroute = json.loads(response.text)
                        vals_log.update({
                            'date_log': datetime.now(),
                            'log_type': 'info',
                            'name': _("API Antsroute : Pickup Request : Pickup created successfully"),
                            'technical_info_4': response.text,
                        })
                        delivery_log = self.env['delivery.carrier.log'].create(vals_log)
                        pick.write({'sent_to_carrier': send_datetime})
                    else:
                        object_antsroute = json.loads(response.text)
                        if object_antsroute and 'status' in object_antsroute and object_antsroute['status'] and 'error' in object_antsroute and object_antsroute['error']:
                            # Error in API we log the details
                            vals_log.update({
                                'date_log':datetime.now(),
                                'log_type':'error',
                                'name':_("API Antsroute : Pickup Request : ERROR [%s] %s") % (response.status_code, object_antsroute['error']),
                            })
                            delivery_log = self.env['delivery.carrier.log'].create(vals_log)
                        elif object_antsroute and 'messages' in object_antsroute and object_antsroute['messages']:
                            vals_log.update({
                                'date_log':datetime.now(),
                                'log_type':'error',
                                'name':_("API Antsroute : Pickup Request : ERROR [%s] %s") % (response.status_code, object_antsroute['messages']),
                            })
                            delivery_log = self.env['delivery.carrier.log'].create(vals_log)
                        elif object_antsroute and 'errorCode' in object_antsroute and object_antsroute['errorCode'] and 'message' in object_antsroute and object_antsroute['message']:
                            vals_log.update({
                                'date_log':datetime.now(),
                                'log_type':'error',
                                'name':_("API Antsroute : Pickup Request : ERROR [%s][%s] %s") % (response.status_code, object_antsroute['errorCode'], object_antsroute['message']),
                            })
                            delivery_log = self.env['delivery.carrier.log'].create(vals_log)
                        else:
                            vals_log.update({
                                'date_log':datetime.now(),
                                'log_type':'error',
                                'name':_("API Antsroute : Pickup Request : Antsroute did not answer, please try again later"),
                            })
                            delivery_log = self.env['delivery.carrier.log'].create(vals_log)
                else:
                    raise UserError(delete)