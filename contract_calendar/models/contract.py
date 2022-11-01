import datetime
import logging

from odoo import models, fields, api, _


_logger = logging.getLogger("------dmitri------")


class Contract(models.Model):
    _inherit = "contract.contract"
    _inherits = {'calendar.event': 'event_id'}
    event_id = fields.Many2one(comodel_name='calendar.event',
                    string='Calendar', auto_join=True, index=True, 
                    ondelete="cascade", required=True)
                    
                    
    @api.model_create_multi
    def create(self, vals_list):
        contracts = self.env["contract.contract"]
        for vals in vals_list:
            _logger.warning(vals_list)
            event = self.env['calendar.event'].create({
                'name': vals.get('name',),
                'start': vals.get('date_start', fields.Date.today()), 
                'duration': 8.0, 
            })
            vals["event_id"] = event.id
            contract = super(Contract, self.with_context()).create(vals)
            event.contract_id = contract.id
            contracts += contract
        self.clear_caches()
        return contracts

    def write(self, values):
        res = super(Contract, self).write(values)
        return res

#TODO: is_calendar for contracts that should have calendar_id so that you can show and not show contracts in calendar

    # ~ def unlink(self):
        # ~ res = super(Contract, self).unlink()
        # ~ return res
    # ~ start = fields.Datetime(related="calendar_id.start")
    # ~ stop = fields.Datetime(related="calendar_id.stop")
    # ~ allday = fields.Boolean(related="calendar_id.allday")
    # ~ start_date = fields.Date(related="calendar_id.start_date")
    # ~ stop_date = fields.Date(related="calendar_id.stop_date")
    # ~ duration = fields.Float(related="calendar_id.duration")
    # ~ description = fields.Text(related="calendar_id.description")
    # ~ privacy = fields.Selection(related="calendar_id.privacy")
    # ~ location = fields.Char(related="calendar_id.location")
    # ~ show_as = fields.Selection(related="calendar_id.show_as")
    # ~ user_id = fields.Many2one(related="calendar_id.user_id")
    # ~ partner_id = fields.Many2one(related="calendar_id.user_id.partner_id")
    # ~ active = fields.Boolean(related="calendar_id.active")
    # ~ categ_ids = fields.Many2many(related="calendar_id.categ_ids")
    # ~ attendee_ids = fields.One2many(related="calendar_id.attendee_ids")

    # ~ # RECURRENCE FIELD
    # ~ recurrency = fields.Boolean(related="calendar_id.recurrency")
    # ~ recurrence_id = fields.Many2one(related="calendar_id.recurrence_id")
    # ~ follow_recurrence = fields.Boolean(related="calendar_id.follow_recurrence")
    # ~ recurrence_update = fields.Selection(related="calendar_id.recurrence_update")

    # ~ # Those field are pseudo-related fields of recurrence_id.
    # ~ # They can't be "real" related fields because it should work at record creation
    # ~ # when recurrence_id is not created yet.
    # ~ # If some of these fields are set and recurrence_id does not exists,
    # ~ # a `calendar.recurrence.rule` will be dynamically created.
    # ~ rrule = fields.Char(related="calendar_id.rrule")
    # ~ rrule_type = fields.Selection(related="calendar_id.rrule_type")
    # ~ event_tz = fields.Selection(related="calendar_id.event_tz")
    # ~ end_type = fields.Selection(related="calendar_id.end_type")
    # ~ interval = fields.Integer(related="calendar_id.interval")
    # ~ count = fields.Integer(related="calendar_id.count")
    # mo = fields.Boolean(related="event_id.mo", readonly=False)
    # ~ tu = fields.Boolean(related="calendar_id.tu")
    # ~ we = fields.Boolean(related="calendar_id.we")
    # ~ th = fields.Boolean(related="calendar_id.th")
    # ~ fr = fields.Boolean(related="calendar_id.fr")
    # ~ sa = fields.Boolean(related="calendar_id.sa")
    # ~ su = fields.Boolean(related="calendar_id.su")
    # ~ month_by = fields.Selection(related="calendar_id.month_by")
    # ~ day = fields.Integer(related="calendar_id.day")
    # ~ weekday = fields.Selection(related="calendar_id.weekday")
    # ~ byday = fields.Selection(related="calendar_id.byday")
    # ~ until = fields.Date(related="calendar_id.until")

