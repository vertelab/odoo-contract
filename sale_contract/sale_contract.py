from openerp import models, fields, api, _


class sale_order(models.Model):
    _inherit = "sale.order"

    # description = fields.Text(related='project_id.analytic_account_id.description', string='Terms')
    # terms_page = fields.Text(related='project_id.analytic_account_id.terms_page', string='Terms Page')


class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    terms_page = fields.Many2one(comodel_name='ir.model.data', domain='(["module", "=", "website"])')


