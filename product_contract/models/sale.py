
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
            # _logger.warning(f"action confirm order: {order}")
            self.create_contracts(order)    
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
            "date_order": self.date_order,
            "date_start": self.date_order.date(),
            "contract_line_fixed_ids": [(0, 0, {
                "product_id": line.product_id.id,
                "name": line.product_id.name,
                "quantity": line.product_uom_qty,
                "price_unit": line.price_unit,
                "uom_id": line.product_uom.id,
            })]
        }
        # _logger.warning(f"inside prepare contract vals {values}")
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

    def create_contracts(self, order):
        # _logger.warning("create_contracts og"*100)
        contracts = self.env["contract.contract"]
        for line in order.order_line:
            # _logger.warning(f"{line=}")
            if line.product_id.is_contract:
                prepare_vals = self._prepare_contract_vals(line)
                contract_id = self.env["contract.contract"].with_context({'from_sale_order': True}).create(prepare_vals)
                # _logger.warning(f"after contract.contract create {contract_id}")
                contract_id.recurring_next_date = contract_id.get_first_invoice_date()
                order.contract_ids = [(4, contract_id.id)]
                line.contract_id = contract_id
                contract_id._onchange_contract_template_id()
                # for cline in contract_id.contract_line_fixed_ids:
                #     cline.quantity *= line.product_uom_qty
                contracts += contract_id
        return contracts