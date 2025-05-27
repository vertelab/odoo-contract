from collections import defaultdict
from odoo import models, fields, api
from odoo.osv import expression


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_contract_vals(self, line):
        contract_id = self.order_line.mapped('product_id')[-1].mapped('contract_id')
        values = {
            "name": f"{self.name} - {self.partner_id.name}",
            "partner_id": self.partner_id.id,
            "invoice_partner_id": self.partner_id.id,
            "sale_id": self.id,
            "user_id": self.user_id.id,
            "total_amount": self.amount_total,
            "contract_payment_type": contract_id.contract_payment_type,
            "final_payment": contract_id.final_payment,
            "down_payment": contract_id.down_payment,
            "contract_line_ids": [(0, 0, {
                "product_id": contract_line.product_id.id,
                "name": contract_line.product_id.name,
                "qty_type": contract_line.qty_type,
                "quantity": contract_line.quantity,
                "price_unit": contract_line.price_unit,
                "uom_id": contract_line.uom_id.id,
            }) for contract_line in contract_id.contract_line_ids]
        }
        return values

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    def _get_delivered_quantity_by_analytic(self, additional_domain):
        """ Compute and write the delivered quantity of current SO lines, based on their related
            analytic lines.
            :param additional_domain: domain to restrict AAL to include in computation (required since timesheet is an AAL with a project ...)
        """
        result = defaultdict(float)

        # avoid recomputation if no SO lines concerned
        if not self:
            return result

        # group analytic lines by product uom and so line
        domain = expression.AND([[('so_line', 'in', self.ids), ('task_id.is_aaw', '=', False)], additional_domain])
        data = self.env['account.analytic.line']._read_group(
            domain,
            ['product_uom_id', 'so_line'],
            ['unit_amount:sum', 'move_line_id:count_distinct', '__count'],
        )

        # convert uom and sum all unit_amount of analytic lines to get the delivered qty of SO lines
        for uom, so_line, unit_amount_sum, move_line_id_count_distinct, count in data:
            if not uom:
                continue
            # avoid counting unit_amount twice when dealing with multiple analytic lines on the same move line
            if move_line_id_count_distinct == 1 and count > 1:
                qty = unit_amount_sum / count
            else:
                qty = unit_amount_sum
            if so_line.product_uom.category_id == uom.category_id:
                qty = uom._compute_quantity(qty, so_line.product_uom, rounding_method='HALF-UP')
            result[so_line.id] += qty

        return result