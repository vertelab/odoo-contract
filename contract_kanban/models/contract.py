from odoo import models, fields, api, _

class Contract(models.Model):
    _inherit = 'contract.contract'

    man_hours_per_month = fields.Float(compute='_compute_man_hours_per_month')

    def _compute_man_hours_per_month(self):
        for rec in self:
            days = rec.mo + rec.tu + rec.we + rec.th + rec.fr + rec.sa + rec.su
            man_hours_per_week = rec.duration * len(rec.partner_ids) * days

            if man_hours_per_week > 0:
                rec.man_hours_per_month = man_hours_per_week * 4 / rec.interval
            else:
                rec.man_hours_per_month = 0
