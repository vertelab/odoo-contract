import datetime
import logging

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


# _logger = logging.getLogger("\33[1;37m\33[45m"+__name__+"\33[1;37m\33[42m")

class RecurrenceRule(models.Model):
    _inherit = "calendar.recurrence"

    contract_id = fields.Many2one(comodel_name='contract.contract', string='Contract')


class Contract(models.Model):
    _inherit = "contract.contract"
    _inherits = {'calendar.event': 'event_id'}

    event_id = fields.Many2one(comodel_name='calendar.event', string='Calendar', auto_join=True,
                               required=True, ondelete='cascade')
    recurrence_event_id = fields.One2many('calendar.recurrence', 'contract_id', string='Recurrence')

    duration = fields.Float('Duration', default=1.0)

    # @api.onchange("date_start")
    # def _inherit_date(self):
    #     self.start = self.date_start
    #     self.start += timedelta(hours=7)
    #     self.start_date = self.date_start
    #     self.stop_date = self.start_date
    #
    # @api.onchange("start_date")
    # def _inherit_stop_date(self):
    #     self.stop_date = self.start_date
    #
    @api.onchange("end_type")
    def _inherit_end_type(self):
        if self.end_type == 'end_date':
            if self.date_end != False:
                self.until = self.date_end

    @api.model_create_multi
    def create(self, vals_list):
        event_list = self.event_vals(vals_list)
        event_id = self.event_id.create(event_list)
        for val in vals_list:
            val.update({'event_id': event_id.id})
        contract = super(Contract, self.with_context()).create(vals_list)

        self.recurrence_event_id = self.event_id.recurrence_id
        return contract

    def write(self, values):
        event_list = self.event_vals(values)
        res = super().write(values)
        recurrences = self.env["calendar.recurrence"].search([
            ('base_event_id.id', 'in', [e.id for e in self])
        ])
        recurrences._select_new_base_event()
        self.event_id.write(event_list)
        return res

    def event_vals(self, values):
        values2_dict = {}
        if isinstance(values, list):
            for val in values:
                for key, item in val.items():
                    if key in self.env['calendar.event']._fields:
                        values2_dict.update({
                            key: item
                        })
        else:
            for key, item in values.items():
                if key in self.env['calendar.event']._fields:
                    values2_dict.update({
                        key: item
                    })
        return values2_dict


# TODO: is_calendar for contracts that should have calendar_id so that you can show and not show contracts in calendar


class ContractLineExtend(models.Model):
    _inherit = 'contract.line'

    location = fields.Char(string="Location")
