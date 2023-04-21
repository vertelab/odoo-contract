from odoo import models, fields

class CustomContractLine(models.Model):
    _inherit = "contract.line"

    def _compute_allowed(self):
        
        super()._compute_allowed()
        
        for rec in self:            
            rec.update(
                {
                    "is_cancel_allowed": True,
                }
            )
            if rec.state == "canceled":
                rec.update(
                {
                    "is_cancel_allowed": False,
                }
            )