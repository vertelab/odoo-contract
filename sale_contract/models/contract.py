from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
import pytz
from odoo import models, fields, api, _
from odoo.addons.calendar.models.calendar_recurrence import (
    weekday_to_field,
    RRULE_TYPE_SELECTION,
    END_TYPE_SELECTION,
    MONTH_BY_SELECTION,
    WEEKDAY_SELECTION,
    BYDAY_SELECTION
)


class Contract(models.Model):
    _inherit = "contract.contract"

    @api.depends("sale_id")
    def _compute_sales_count(self):
        for rec in self:
            if rec.sale_id:
                rec.sale_count = len(rec.sale_id)
            else:
                rec.sale_count = 0

    @api.depends("name")
    def _compute_calendar_count(self):
        for rec in self:
            rec.calendar_ids = self.env["calendar.event"].search([("contract_id", "=", self.id)]).ids
            rec.calendar_count = len(rec.calendar_ids)

    sale_id = fields.Many2one("sale.order", string="Sale")
    sale_count = fields.Integer(string="Sale Count", compute=_compute_sales_count)

    calendar_ids = fields.Many2many("calendar.event", string="Schedule", compute=_compute_calendar_count)
    calendar_count = fields.Integer(string="Calendar Count", compute=_compute_calendar_count)

    # SCHEDULE FIELD
    recurrency = fields.Boolean('Recurrent', help="Recurrent Event")
    end_type = fields.Selection(END_TYPE_SELECTION, string='Recurrence Termination', readonly=False, default='count')
    count = fields.Integer(string='Repeat', help="Repeat x times", readonly=False, default=1)
    interval = fields.Integer(string='Repeat Every', help="Repeat every (Days/Week/Month/Year)", default=1)
    rrule_type = fields.Selection(RRULE_TYPE_SELECTION, string='Recurrence',
                                  help="Let the event automatically repeat at that interval", readonly=False,
                                  default='weekly')

    month_by = fields.Selection(MONTH_BY_SELECTION, string='Option', readonly=False, default='date')
    day = fields.Integer('Date of month', readonly=False)
    weekday = fields.Selection(WEEKDAY_SELECTION, readonly=False, default='TU')
    byday = fields.Selection(BYDAY_SELECTION, readonly=False, default='3')
    until = fields.Date(string="Until")

    mo = fields.Boolean('Mon', readonly=False)
    tu = fields.Boolean('Tue', readonly=False)
    we = fields.Boolean('Wed', readonly=False)
    th = fields.Boolean('Thu', readonly=False)
    fr = fields.Boolean('Fri', readonly=False)
    sa = fields.Boolean('Sat', readonly=False)
    su = fields.Boolean('Sun', readonly=False)

    duration = fields.Float('Duration')

    start = fields.Datetime(
        'Start', required=True, tracking=True, default=fields.Date.today,
        help="Start date of an event, without time for full days events")
    stop = fields.Datetime(
        'Stop', required=True, tracking=True, default=lambda self: fields.Datetime.today() + timedelta(hours=1),
        readonly=False, store=True,
        help="Stop date of an event, without time for full days events")

    def action_view_sales(self):
        self.ensure_one()
        ctx = dict(self.env.context)

        action = {
            "type": "ir.actions.act_window",
            "name": "Contract Sale",
            "res_model": "sale.order",
            "view_mode": "form",
            "domain": [("id", "=", self.sale_id.id)],
            'res_id': self.sale_id.id,
            "context": ctx,
        }
        return action

    def action_create_calendar(self):
        calendar_event_id = self.env["calendar.event"].create(self._prepare_event_calendar_values())
        self.calendar_ids = [(4, calendar_event_id.id)]
        return calendar_event_id

    def _prepare_event_calendar_values(self):
        start = datetime.strftime(fields.Datetime.context_timestamp(self, self.start), "%Y-%m-%d %H:%M:%S")
        stop = datetime.strftime(fields.Datetime.context_timestamp(
            self, self.start + relativedelta(hours=self.duration)), "%Y-%m-%d %H:%M:%S")
        values = {
            "name": f"{self.name}",
            "partner_ids": [(4, self.partner_id.id)],
            "start": start,
            "stop": stop,
            "duration": self.duration,
            "user_id": self.user_id.id,
            "show_as": "busy",
            "contract_id": self.id,
        }
        if self.recurrency:
            values.update({
                "recurrency": self.recurrency,
                "interval": self.interval,
                "rrule_type": self.rrule_type,
                "end_type": self.end_type,
                "count": self.count,
                "month_by": self.month_by,
                "byday": self.byday,
                "weekday": self.weekday,
                "mo": self.mo,
                "tu": self.tu,
                "we": self.we,
                "th": self.th,
                "fr": self.fr,
                "sa": self.sa,
                "su": self.su,
                "until": self.until
            })
        return values

    def action_view_schedules(self):
        self.ensure_one()
        tree_view = self.env.ref("calendar.view_calendar_event_tree", raise_if_not_found=False)
        form_view = self.env.ref("calendar.view_calendar_event_form", raise_if_not_found=False)
        calendar_view = self.env.ref("sale_contract.view_calendar_event_calendar_month_mode", raise_if_not_found=False)
        ctx = dict(self.env.context)

        action = {
            "type": "ir.actions.act_window",
            "name": "Contract Schedule",
            "res_model": "calendar.event",
            "view_mode": "calendar,tree,form",
            "domain": [("id", "in", self.calendar_ids.ids)],
            "context": ctx,
        }
        if tree_view and form_view and calendar_view:
            action["views"] = [(calendar_view.id, "calendar"), (tree_view.id, "tree"), (form_view.id, "form")]
        return action
