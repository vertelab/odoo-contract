import odoorpc
import xmlrpc.client

from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class Contract(models.Model):
    _inherit = 'contract.contract'

    def get_quests(self):
        if self.partner_id:
            odoo = self.get_rpc_connection()
            quests = 0
            try:
                quests = odoo.env["ai.quest"].get_xmlrpc_quests()
            except:
                raise UserError("Could not get quest information. Make sure ai_agent is installed on the customer machine.")
            return quests
