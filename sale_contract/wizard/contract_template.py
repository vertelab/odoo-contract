from openerp import models, fields, api, _
from datetime import datetime
from openerp import tools
import logging

_logger = logging.getLogger(__name__)


class sale_contract_wizard(models.TransientModel):
    _name = 'sale.contract.wizard'

    template_id = fields.Many2one(comodel_name='account.analytic.account', string='Template of Contract')

    @api.one
    def create_contract(self):
        service = self.env['product.product'].search([('type', '=', 'service')])
        goods = self.env['product.product'].search([('type', '=', 'consu')])
        _logger.warning('<<<<<<<<<<< SERVICE >>>>>>>>>>>: %s' % service)
        _logger.warning('<<<<<<<<<<< GOODS >>>>>>>>>>>: %s' % goods)

        for order in self.env['sale.order'].browse(self._context.get('active_ids')):
            # copy a record from a template to a contract
            contract = self.template_id.copy({
                'date_start': fields.date.today(),
                # 'amount_max': sum([l.price_subtotal for l in order.order_line.product_id]),  # TODO: find out the product ids of goods
                # 'hours_qtt_est': sum([l.price_subtotal for l in order.order_line.product_id]),  # TODO: find out the product ids of service
                'invoice_on_timesheets': True,
                'type': 'template',
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