import logging
import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class AgreementContractWizard(models.TransientModel):
    _inherit = "agreement.contract.wizard"
    
    def _generate_contract(self, agreement, price_list):
        res = super()._generate_contract(agreement,price_list)
        if self.agreement_id.booking_resource_id:
           self.agreement_id.make_resource_unavailable()
        return res 
        
