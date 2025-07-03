from odoo import models, fields, api, _


class ProjectTask(models.Model):
    _inherit = "project.task"

    ## Need to be set by task
    is_aaw = fields.Boolean(string="Is AAW")

    is_signed = fields.Boolean(string="AAW Signed", readonly=True)

    def action_request_signature(self):
        self.ensure_one()

        render_result = self.env["ir.qweb"]._render(
            "contract_aaw.aaw_sign_template_mail",
            {
                "record": self.partner_id,
                "link": self.access_url,
                "sender": self.env.user
            },
            engine="ir.qweb",
            minimal_qcontext=True,
        )

        self.message_post(
            author_id=self.partner_id.id,
            partner_ids=self.partner_id.ids,
            subject=self.env._("New document to sign"),
            body=render_result,
            message_type="notification",
            mail_auto_delete=False,
            email_layout_xmlid="mail.mail_notification_light"
        )


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
