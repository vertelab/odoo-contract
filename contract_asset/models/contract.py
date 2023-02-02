from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class Contract(models.Model):
    _inherit = 'contract.contract'

    account_asset_id = fields.Many2one('account.asset', string="Account Asset")
    rent_rate = fields.Float(string="Rate Percentage")

    @api.constrains('rent_rate')
    def _check_something(self):
        for record in self:
            if record.rent_rate > 100:
                raise ValidationError("Percentage cannot be more than 100%")


class ContractLine(models.Model):
    _inherit = 'contract.line'

    def _prepare_invoice_line(self, move_form):
        self.ensure_one()
        dates = self._get_period_to_invoice(
            self.last_date_invoiced, self.recurring_next_date
        )
        line_form = move_form.invoice_line_ids.new()
        line_form.display_type = self.display_type
        line_form.product_id = self.product_id
        invoice_line_vals = line_form._values_to_save(all_fields=True)
        name = self._insert_markers(dates[0], dates[1])
        invoice_line_vals.update(
            {
                "account_id": invoice_line_vals["account_id"]
                if "account_id" in invoice_line_vals and not self.display_type
                else False,
                "quantity": self._get_quantity_to_invoice(*dates),
                "product_uom_id": self.uom_id.id,
                "discount": self.discount,
                "contract_line_id": self.id,
                "sequence": self.sequence,
                "name": name,
                "analytic_account_id": self.analytic_account_id.id,
                "analytic_tag_ids": [(6, 0, self.analytic_tag_ids.ids)],
                "price_unit": self.price_unit,
            }
        )

        if not self.contract_id.account_asset_id:
            raise ValidationError(_("No asset is associated with this contract"))
        if self.contract_id.account_asset_id and self.contract_id.account_asset_id.state != 'open':
            raise ValidationError(_("You have no running contract"))

        depreciation_line_id = self.contract_id.account_asset_id.depreciation_line_ids.filtered(
                lambda line: line.line_date == self.recurring_next_date)
        if self.product_id.type == 'rent':
            invoice_line_vals['price_unit'] = (depreciation_line_id.amount + depreciation_line_id.remaining_value) * \
                                              ((self.contract_id.rent_rate/100)/self.contract_id.account_asset_id.method_number)
        elif self.product_id.type == 'amortization':
            invoice_line_vals['price_unit'] = depreciation_line_id.amount

        return invoice_line_vals
