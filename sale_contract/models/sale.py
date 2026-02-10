from odoo import models, fields, api, _


class Sale(models.Model):
    _inherit = "sale.order"

    contract_ids = fields.Many2many("contract.contract", string="Contract", copy=False)

    @api.depends("contract_ids")
    def _compute_contract_count(self):
        for rec in self:
            if rec.contract_ids:
                rec.contract_count = len(rec.contract_ids)
                rec.is_contract = True
            else:
                rec.contract_count = 0
                rec.is_contract = False

    is_contract = fields.Boolean(string="Has Contract")
    contract_count = fields.Integer(string="Contract Count", compute=_compute_contract_count)

    # def _action_confirm(self):
    #     """ On SO confirmation, some lines should generate a contract. """
    #     result = super(Sale, self)._action_confirm()
    #     self.action_create_contract()
    #     return result

    # def action_create_contract(self):
    #     contract_id = self.env["contract.contract"].create(self._prepare_contract_vals())
    #     self.contract_ids = [(4, contract_id.id)]
    #     return contract_id

    def _prepare_contract_vals(self, line):
        values = {
            "name": f"{self.name} - {self.partner_id.name}",
            "partner_id": self.partner_id.id,
            "invoice_partner_id": self.partner_id.id,
            "sale_id": self.id,
            "user_id": self.user_id.id,
            "contract_line_fixed_ids": [(0, 0, self._prepare_contract_line_vals(line)) for line in self.order_line]
        }
        return values

    def _prepare_contract_line_vals(self, line):
        return {
            "product_id": line.product_id.id,
            "name": line.product_id.name,
            "quantity": line.product_uom_qty,
            "price_unit": line.price_unit,
            "sale_order_line_id": line.id,
        }


    # def action_view_contract(self):
    #     self.ensure_one()
    #     tree_view = self.env.ref("contract.contract_contract_tree_view", raise_if_not_found=False)
    #     form_view = self.env.ref("contract.contract_contract_customer_form_view", raise_if_not_found=False)
    #     ctx = dict(self.env.context)
    #
    #     action = {
    #         "type": "ir.actions.act_window",
    #         "name": "Sale Contracts",
    #         "res_model": "contract.contract",
    #         "view_mode": "form",
    #         "domain": [("id", "in", self.contract_ids.ids)],
    #         "context": ctx,
    #     }
    #     if tree_view and form_view:
    #         action["views"] = [(tree_view.id, "list"), (form_view.id, "form")]
    #     return action


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    contract_id = fields.Many2one(
        comodel_name='contract.contract', string='Contract', domain=[('type', '=', 'contract')]
    )
