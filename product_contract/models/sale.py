
import logging
_logger = logging.getLogger(__name__)

from odoo import models, fields, api, _


class Sale(models.Model):
    _inherit = "sale.order"

    contract_ids = fields.Many2many("contract.contract", string="Contract")
    
    @api.depends("contract_ids")
    def _compute_contract_count(self):
        for rec in self:
            if rec.contract_ids:
                rec.contract_count = len(rec.contract_ids)
            else:
                rec.contract_count = 0    
    contract_count = fields.Integer(string="Contract Count", compute=_compute_contract_count)
    
    
    
    def _action_confirm(self):
        """ On SO confirmation, some lines should generate a contract. """
        result = super(Sale,self)._action_confirm()
        for order in self:
            for line in order.order_line:
                if line.product_id.is_contract:
                    contract_id = self.env["contract.contract"].create(self._prepare_contract_vals(line))
                    contract_id.recurring_next_date = contract_id.get_first_invoice_date()
                    order.contract_ids = [(4, contract_id.id)]
                    line.contract_id = contract_id
                    contract_id._onchange_contract_template_id()
                    for cline in contract_id.contract_line_fixed_ids:
                        cline.quantity *= line.product_uom_qty
        return result
        
    def _prepare_contract_vals(self,line):
        values = {
            "name": f"{self.name} - {self.partner_id.parent_id.name if self.partner_id.parent_id else self.partner_id.name }",
            "partner_id": self.partner_id.id,
            "invoice_partner_id": self.partner_id.id,
            "sale_id": self.id,
            "user_id": self.user_id.id,
            "contract_template_id": line.product_id.product_tmpl_id.contract_id.id,
            "recurring_next_date": fields.Date.today(),
        }
        return values

    def action_view_contract(self):
        self.ensure_one()
        tree_view = self.env.ref("contract.contract_contract_tree_view", raise_if_not_found=False)
        form_view = self.env.ref("contract.contract_contract_customer_form_view", raise_if_not_found=False)
        ctx = dict(self.env.context)

        action = {
            "type": "ir.actions.act_window",
            "name": "Sale Contracts",
            "res_model": "contract.contract",
            "view_mode": "form",
            "domain": [("id", "in", self.contract_ids.ids)],
            "context": ctx,
        }
        if tree_view and form_view:
            action["views"] = [(tree_view.id, "tree"), (form_view.id, "form")]
        return action