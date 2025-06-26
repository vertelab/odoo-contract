from odoo import models, fields, api, _


class Sale(models.Model):
    _inherit = "sale.order"

    @api.depends("contract_ids")
    def _compute_contract_count(self):
        for rec in self:
            if rec.contract_ids:
                rec.contract_count = len(rec.contract_ids)
            else:
                rec.contract_count = 0

    contract_ids = fields.Many2many("contract.contract", string="Contract")
    contract_count = fields.Integer(string="Contract Count", compute=_compute_contract_count)

    def action_create_contract(self):
        contract_id = self.env["contract.contract"].create(self._prepare_contract_vals())
        self.contract_ids = [(4, contract_id.id)]
        return contract_id

    def _prepare_contract_vals(self):
        values = {
            "name": f"{self.name} - {self.partner_id.name}",
            "partner_id": self.partner_id.id,
            "invoice_partner_id": self.partner_id.id,
            "sale_id": self.id,
            "user_id": self.user_id.id,
            "contract_line_fixed_ids": [(0, 0, {
                "product_id": line.product_id.id,
                "name": line.product_id.name,
                "quantity": line.product_uom_qty,
                "price_unit": line.price_unit,
            }) for line in self.order_line]
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