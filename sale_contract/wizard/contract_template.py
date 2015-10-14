from openerp import models, fields, api, _
from datetime import datetime
from openerp import tools
import logging

_logger = logging.getLogger(__name__)


class sale_contract_wizard(models.TransientModel):
    _name = 'sale.contract.wizard'

    template_id = fields.Many2one(comodel_name='account.analytic.account', string='Template of Contract', domain=(['type', '=', 'template']))

    @api.one
    def create_contract(self):
        categ_wtime = self.env.ref('product.uom_categ_wtime')  # Working time-type
        service_uom = [c.id for c in self.env['product.uom'].search([('category_id', '=', categ_wtime.id)])]  # All uom of working time type
        service_products = [p.id for p in self.env['product.product'].search([('type', '=', 'service'), ('uom_id', 'in', service_uom)])]
        other_products = [p.id for p in self.env['product.product'].search([]) if p.id not in service_products]

        for order in self.env['sale.order'].browse(self._context.get('active_ids')):
            # copy a record from a template to a contract
            contract = self.template_id.copy({
                'partner_id': order.partner_id.id,
                'manager_id': self._uid,
                'date_start': fields.date.today(),
                'amount_max': sum([l.price_subtotal for l in order.order_line if l.product_id.id in other_products]),
                'hours_qtt_est': sum([l.price_subtotal for l in order.order_line if l.product_id.id in service_products]),
                'invoice_on_timesheets': True,
                'type': 'contract',
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


class project(models.Model):
    _inherit = 'project.project'
