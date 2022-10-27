from odoo import models, fields, api, _


class Calendar(models.Model):
    _inherit = "calendar.event"

    @api.depends("contract_id")
    def _compute_contract_count(self):
        for rec in self:
            if rec.contract_id:
                rec.contract_count = len(rec.contract_id)
            else:
                rec.contract_count = 0

    contract_id = fields.Many2one("contract.contract", string="Contract")
    contract_count = fields.Integer(string="Contract Count", compute=_compute_contract_count)

    def action_view_contract(self):
        self.ensure_one()
        action = {
            "type": "ir.actions.act_window",
            "name": "Contract",
            "res_model": "contract.contract",
            "view_mode": "form",
            "domain": [("id", "in", self.contract_id.id)],
            "res_id": self.contract_id.id,
            "context": dict(self.env.context),
        }
        return action
