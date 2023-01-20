from odoo import api, models, fields, _
import logging
_logger = logging.getLogger(__name__)

class Contract(models.Model):
    
    _inherit = 'contract.contract'
    
    employee_skill_ids = fields.One2many('hr.employee.skill' ,inverse_name='employee_contract_id', string="Skills")
    

      
class ResPartner(models.Model):
    
    _inherit = "hr.employee.skill"
    
    employee_contract_id = fields.Many2one('contract.contract', string="Parent", tracking=True) 
    
    
    
     
    # @api.model_create_multi
    # def create(self, vals_list):
    #     res = super(Employee, self).create(vals_list)
    #     resume_lines_values = []
    #     for employee in res:
    #         line_type = self.env.ref('hr_skills.resume_type_experience', raise_if_not_found=False)
    #         resume_lines_values.append({
    #             'employee_id': employee.id,
    #             'name': employee.company_id.name or '',
    #             'date_start': employee.create_date.date(),
    #             'description': employee.job_title or '',
    #             'line_type_id': line_type and line_type.id,
    #         })
    #     self.env['hr.resume.line'].create(resume_lines_values)
      #     return res