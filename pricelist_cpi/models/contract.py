from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)

class Contract(models.Model):
    _inherit = "contract.contract"

    consumer_index_base_year_id = fields.Many2one("consumer.price.index", string="Price Base Index")

    def _get_price_rule(self, sub_line):
        price_rule = self.pricelist_id.item_ids.filtered(
            lambda item: item.date_start.date() <= sub_line.period_date_end and
                         sub_line.date <= item.date_end.date()
        )
        print("price_rule", price_rule)
        return price_rule

    def _index_computation(self, stub_line):
        price_rule = self._get_price_rule(stub_line)

        agreement_index = self.consumer_index_base_year_id.index
        current_index = self.env['consumer.price.index'].search([('year', '=', stub_line.date.year - 1)]).index # subline year - 1

        if current_index <= agreement_index:
            return price_rule.fixed_price

        index_diff = current_index - agreement_index
        index_quota = index_diff / agreement_index
        return price_rule.fixed_price + (index_quota * price_rule.fixed_price)

    def compute_contract(self):
        """Main method to compute contract invoice stubs"""
        self._clear_uninvoiced_lines()

        invoicing_date = self._get_starting_date()
        date_end = self._get_end_date(invoicing_date)

        while invoicing_date and (invoicing_date <= date_end):
            _logger.warning(f"Running while with invoicing date: {invoicing_date}")

            stub_line = self._process_stub_for_date(invoicing_date)
            if stub_line:
                index_amount = self._index_computation(stub_line)
                stub_line.write({'amount': index_amount})

            invoicing_date = self._get_next_invoicing_date(invoicing_date)


    def _process_stub_for_date(self, invoicing_date):
        """Create or update stub for given date"""
        existing_stub = self.env['contract.invoice.stub'].search([
            ('contract_id', '=', self.id),
            ('date', '=', invoicing_date),
        ])

        stub_amount = self._compute_contract_lines()

        if not existing_stub:
            stub_line = self.env['contract.invoice.stub'].create({
                'amount': stub_amount,
                'date': invoicing_date,
                'period_date_end': self.get_next_period_date_end(
                    invoicing_date, self.recurring_rule_type,
                    self.recurring_interval, max_date_end=self.date_end
                ),
                'contract_id': self.id
            })
            return stub_line
        elif not existing_stub.account_move_id:
            existing_stub.write({'amount': stub_amount})
            return existing_stub
        return False



class ContractInvoiceSub(models.Model):
    _inherit = 'contract.invoice.stub'

    def action_create_move(self):
        if self.account_move_id:
            return
        self.contract_id.write({
            'active_stub_start_date': self.date,
            'active_stub_end_date': self.period_date_end,
        })

        if not self.contract_id.consumer_index_base_year_id:
            self.amount = self.contract_id._compute_contract_lines()

        self.contract_id._set_contract_line_next_period_date(self)
        invoices = self.contract_id._recurring_create_invoice(self.date)
        for invoice in invoices:
            # invoice.invoice_date = fields.Date.today()
            # ~ invoice.period_id = self.env['account.period'].date2period(invoice.invoice_date)
            invoice.message_post(
                body=_(
                    "Contract manually invoiced by stubs: "
                    '<a href="#" data-oe-model="%s" data-oe-id="%s">Invoice'
                    "</a>"
                )
                     % (invoice._name, invoice.id),
                subtype_id=self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note'),
            )
            self.write({
                'account_move_id': invoice.id,
            })

        self.account_move_id.write({
            'contract_stub_id': self.id,
            'contract_id': self.contract_id.id,
        })

        self.contract_id.write({
            'recurring_next_date': self._get_next_recurring_date().date if self._get_next_recurring_date() else self.date
        })
        self.contract_id._set_uninvoiced_stubs()


class ContractInvoiceLine(models.Model):
    _inherit = 'contract.line'

    def _prepare_invoice_line(self):
        self.ensure_one()
        dates = self._get_period_to_invoice(
            self.last_date_invoiced, self.recurring_next_date
        )
        name = self._insert_markers(dates[0], dates[1])
        return {
            "quantity": self._get_quantity_to_invoice(*dates),
            "product_uom_id": self.uom_id.id,
            "discount": self.discount,
            "contract_line_id": self.id,
            "analytic_distribution": self.analytic_distribution,
            "sequence": self.sequence,
            "name": name,
            "price_unit": self._get_sub_price(self.last_date_invoiced), # self.price_unit,
            "display_type": self.display_type or "product",
            "product_id": self.product_id.id,
        }

    def _get_sub_price(self, current_date):
        date_stub = self.contract_id.invoice_stub_ids.filtered(
            lambda stub: stub.date <= self.recurring_next_date <= stub.period_date_end
        )

        return date_stub.amount