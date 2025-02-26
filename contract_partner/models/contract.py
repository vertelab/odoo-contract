import odoorpc
import xmlrpc.client

from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class Contract(models.Model):
    _inherit = 'contract.contract'

    def get_rpc_connection(self):
        if self.partner_id.customer_url and self.partner_id.customer_db:
            odoo = odoorpc.ODOO(self.partner_id.customer_url, port=8069)

            dbs = odoo.db.list()
            db = ""

            try:
                db = dbs[dbs.index(self.partner_id.customer_db)]
            except ValueError:
                raise UserError(_("The customer database set on the customer does not seem to exist on the set customer endpoint."))

            password = tools.config.get(f"{self.partner_id.name}_password")

            if not password:
                raise UserError(_("There doesn't seem to be any customer password set in the odoo.conf file for this customer."))

            try:
                odoo.login(db, 'admin', f'{password}')
            except ValueError:
                raise UserError(_("Login failed. Are you sure you have the correct password for the specified customer in the odoo.conf file?"))

            return odoo
    
        raise UserError("Customer database or customer endpoint not set on customer")

    def get_paid_users(self):
        if self.partner_id:
            odoo = self.get_rpc_connection()
            users = odoo.env["res.users"].search_count([("login", "!=", "admin")])
            return users


       
