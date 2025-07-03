from odoo import models, fields, api, _


class ContractTemplate(models.Model):
    _inherit = 'contract.template'

    is_aaw = fields.Boolean(string="Is AAW")

    contract_payment_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed')], string="Contract Type", default='percentage')

    down_payment = fields.Float(string="Down Payment (%)")
    final_payment = fields.Float(string="Final Payment (%)")
    total_amount = fields.Float(string="Total Amount")
    fixed_amount = fields.Float(string="Fixed Amount")



