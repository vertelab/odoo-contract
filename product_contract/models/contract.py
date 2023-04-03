import datetime
import logging

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _


_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = "contract.contract"
    
    @api.depends("sale_order_line_id","sale_order_line_id.task_id","sale_order_line_id.project_id")
    def compute_project_id(self):
        _logger.warning("compute_project_id"*100)
        for rec in self:
            _logger.warning(f"{rec=} {rec.sale_order_line_id.task_id=} {rec.sale_order_line_id.project_id=}")
            if rec.sale_order_line_id.task_id:
                rec.project_id = rec.sale_order_line_id.task_id.project_id
            else:
                rec.project_id = rec.sale_order_line_id.project_id
   
    sale_id = fields.Many2one(comodel_name='sale.order')
    sale_order_line_id = fields.Many2one(comodel_name='sale.order.line') 
    project_id = fields.Many2one(comodel_name="project.project", compute="compute_project_id", store=True)
    


    def get_first_invoice_date(self):
        """Return the date of the first invoice"""
        today = fields.Date.from_string(fields.Date.today())
        time = fields.Date.from_string(self.recurring_next_date)
        if self.recurring_rule_type == 'daily':
            deltaT = relativedelta(days = self.recurring_interval)
        elif self.recurring_rule_type == 'weekly':
            deltaT = relativedelta(weeks = self.recurring_interval)
        elif self.recurring_rule_type == 'monthly':
            deltaT = relativedelta(months = self.recurring_interval)
        elif self.recurring_rule_type == 'yearly':
            deltaT = relativedelta(years = self.recurring_interval)
        while time < today:
            time += deltaT
        
        #First invoice is generated by the product, so skip to the second invoice here
        time += deltaT
        
        return fields.Date.to_string(time)
    
    
