from openerp import models, fields, api, _
from datetime import datetime
from openerp import tools


class sale_contract_wizard(models.TransientModel):
    _name = 'sale.contract.wizard'

    template_id = fields.Many2one(comodel_name='account.analytic.account', string='Template of Contract')

    @api.one
    def create_contract(self):
        for order in self.env['sale.order'].browse(self._context.get('active_ids')):
            # skapa en record fran template (copy)
            contract = self.template_id.copy({
                'date_start': fields.date.today(),
                'hours_qtt_est': sum([l.price_subtotal for l in order.order_line]),
                'invoice_on_timesheets': True,
            })
            if self.template_id.date_start and self.template_id.date:
                from_dt = datetime.strptime(self.template_id.date_start, tools.DEFAULT_SERVER_DATE_FORMAT)
                to_dt = datetime.strptime(self.template_id.date, tools.DEFAULT_SERVER_DATE_FORMAT)
                timedelta = to_dt - from_dt
                contract.date = datetime.strftime(datetime.now() + timedelta, tools.DEFAULT_SERVER_DATE_FORMAT)
            if not self.template_id.date_start:
                contract.date_start = fields.date.today()
            contract.name = order.name
            order.project_id = contract
