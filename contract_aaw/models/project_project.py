from collections import defaultdict
from odoo import models, api, fields, _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    is_aaw = fields.Boolean(string="Is AAW")

    total_aaw_timesheet_time = fields.Integer(
        compute='_compute_total_aaw_timesheet_time', groups='hr_timesheet.group_hr_timesheet_user',
        string="Total number of time (in the proper UoM) recorded in the project, rounded to the unit.",
        compute_sudo=True, export_string_translation=False)

    def _compute_total_aaw_timesheet_time(self):
        timesheets_read_group = self.env['account.analytic.line']._read_group(
            [('project_id', 'in', self.ids), ('task_id.is_aaw', '=', True)],
            ['project_id', 'product_uom_id'],
            ['unit_amount:sum'],
        )
        timesheet_time_dict = defaultdict(list)
        for project, product_uom, unit_amount_sum in timesheets_read_group:
            timesheet_time_dict[project.id].append((product_uom, unit_amount_sum))

        for project in self:
            # Timesheets may be stored in a different unit of measure, so first
            # we convert all of them to the reference unit
            # if the timesheet has no product_uom_id then we take the one of the project
            total_time = 0.0
            for product_uom, unit_amount in timesheet_time_dict[project.id]:
                factor = (product_uom or project.timesheet_encode_uom_id).factor_inv
                total_time += unit_amount * (1.0 if project.encode_uom_in_days else factor)
            # Now convert to the proper unit of measure set in the settings
            total_time *= project.timesheet_encode_uom_id.factor
            project.total_aaw_timesheet_time = int(round(total_time))

    def _compute_total_timesheet_time(self):
        timesheets_read_group = self.env['account.analytic.line']._read_group(
            [('project_id', 'in', self.ids), ('task_id.is_aaw', '=', False)],
            ['project_id', 'product_uom_id'],
            ['unit_amount:sum'],
        )
        timesheet_time_dict = defaultdict(list)
        for project, product_uom, unit_amount_sum in timesheets_read_group:
            timesheet_time_dict[project.id].append((product_uom, unit_amount_sum))

        for project in self:
            # Timesheets may be stored in a different unit of measure, so first
            # we convert all of them to the reference unit
            # if the timesheet has no product_uom_id then we take the one of the project
            total_time = 0.0
            for product_uom, unit_amount in timesheet_time_dict[project.id]:
                factor = (product_uom or project.timesheet_encode_uom_id).factor_inv
                total_time += unit_amount * (1.0 if project.encode_uom_in_days else factor)
            # Now convert to the proper unit of measure set in the settings
            total_time *= project.timesheet_encode_uom_id.factor
            project.total_timesheet_time = int(round(total_time))



    def _get_stat_buttons(self):
        buttons = super(ProjectProject, self)._get_stat_buttons()
        encode_uom = self.env.company.timesheet_encode_uom_id
        aaw_timesheet = self.total_aaw_timesheet_time
        if not self.allow_timesheets or not self.env.user.has_group("hr_timesheet.group_hr_timesheet_user"):
            return buttons

        color = ""

        if aaw_timesheet > 0:
            buttons.append({
                "icon": f"clock-o {color}",
                "text": self.env._("AAW Sheet"),
                "number": self.env._(
                    "%(aaw_hours)s %(uom_name)s",
                    aaw_hours=round(aaw_timesheet),
                    uom_name=encode_uom.name,
                ),
                "action_type": "object",
                "action": "act_hr_timesheet_line_by_aaw_project",
                "show": True,
                "sequence": 4,
            })
        return buttons

    def act_hr_timesheet_line_by_aaw_project(self):
        action = self.env['ir.actions.act_window']._for_xml_id('contract_aaw.act_hr_timesheet_line_by_aaw_project')
        action['display_name'] = _("%(name)s's Timesheets - AAW", name=self.name)
        return action
