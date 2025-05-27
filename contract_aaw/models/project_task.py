from odoo import models, fields, api, _


class ProjectTask(models.Model):
    _inherit = "project.task"

    is_aaw = fields.Boolean(string="Is AAW")

    def _compute_remaining_hours_so(self):
        # TODO This is not yet perfectly working as timesheet.so_line stick to its old value although changed
        #      in the task From View.
        timesheets = self.timesheet_ids.filtered(
            lambda t: not t.task_id.is_aaw
                      and t.task_id.sale_line_id in (t.so_line, t._origin.so_line)
                      and t.so_line.remaining_hours_available
        )

        mapped_remaining_hours = {
            task._origin.id: task.sale_line_id and task.sale_line_id.remaining_hours or 0.0 for task in self
        }
        uom_hour = self.env.ref('uom.product_uom_hour')
        for timesheet in timesheets:
            delta = 0
            if timesheet._origin.so_line == timesheet.task_id.sale_line_id:
                delta += timesheet._origin.unit_amount
            if timesheet.so_line == timesheet.task_id.sale_line_id:
                delta -= timesheet.unit_amount
            if delta:
                mapped_remaining_hours[
                    timesheet.task_id._origin.id] += timesheet.product_uom_id._compute_quantity(delta, uom_hour)

        for task in self:
            task.remaining_hours_so = mapped_remaining_hours[task._origin.id]