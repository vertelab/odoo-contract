import datetime
import logging

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

# ~ _logger = logging.getLogger(__name__)
_logger = logging.getLogger("\33[1;37m\33[45m"+__name__+"\33[1;37m\33[42m")


class RecurrenceRule(models.Model):
    _inherit = "calendar.recurrence"
    contract_id = fields.Many2one(comodel_name='contract.contract', string='Contract')


class Contract(models.Model):
    _inherit = "contract.contract"
    _inherits = {'calendar.event': 'event_id'}
    event_id = fields.Many2one(comodel_name='calendar.event', string='Calendar')
    recurrence_event_id = fields.One2many(comodel_name='calendar.recurrence', inverse_name='contract_id', string='Recurrence')
    duration = fields.Float('Duration', default = 1.0)

    @api.onchange("date_start")
    def _inherit_date(self):
        self.start = self.date_start
        self.start += timedelta(hours=7)
        self.start_date = self.date_start

    @api.onchange("start_date")
    def _inherit_stop_date(self):
        self.stop_date = self.start_date

    @api.onchange("end_type")
    def _inherit_end_type(self):
        if self.end_type == 'end_date':
            if self.date_end != False:
                self.until = self.date_end

    @api.model_create_multi
    def create(self, vals_list):
        event_list = self.event_vals(vals_list)
        contract = super(Contract, self.with_context()).create(vals_list)
        self.event_id.create(event_list)
        self.recurrence_event_id = self.event_id.recurrence_id
        return contract

    def write(self, values):
        event_list = self.event_vals(values)
        res = super().write(values)
        recurrences = self.env["calendar.recurrence"].search([
            ('base_event_id.id', 'in', [e.id for e in self])
        ])
        _logger.error(f"{recurrences=}")
        # ~ if recurrences:
        _logger.error(f"{recurrences._select_new_base_event()=}")
        _logger.error(f"{recurrences=}")
        recurrences._select_new_base_event()
        _logger.error(f"{recurrences._select_new_base_event()=}")
        self.event_id.write(event_list)
        return res

    def event_vals(self, values):
        if type(values) == list:
            _logger.error(f"First{values=}")
            # ~ _logger.error(f"{values[{'start'}]=}")
            values2 = []
            for val2 in values:
                values2_dict = {}
                # ~ _logger.error(f"{values2_dict.get('start')=}")
                _logger.error(f"{val2.get('start')=}")
                # ~ _logger.error(f"{timedelta(hours=val2.get('duration'))=}")
                for key_field in val2:
                    if key_field in self.env['calendar.event']._fields:
                        values2_dict[key_field] = val2[key_field]
                        values2_dict.update({
                                                    'name': self.name, 
                                                    'duration': self.duration, 
                                                    'stop': datetime.strptime(str(val2.get('start')), '%Y-%m-%d %H:%M:%S').date() + timedelta(hours=self.duration), 
                                                    'start': datetime.strptime(str(val2.get('start')), '%Y-%m-%d %H:%M:%S').date(),
                                                    })
                        _logger.error(f"{values2_dict=}")
                values2.append(values2_dict)
            # ~ values2_dict.update({'name': self.name, 'duration': self.duration, 'stop': self.start + timedelta(hours='duration'),})
            _logger.error(f"First{values2=}")
            return values2
        else:
            values2 = {}
            for key_field in values:
                _logger.error(f"Secund{values=}")
                if key_field in self.env['calendar.event']._fields:
                    values2[key_field] = values[key_field]
            # ~ val_name = {'name': self.name}
            # ~ _logger.error(f"{val_name=}")
            values2.update({
                                'name': self.name, 
                                'duration': self.duration, 
                                'stop': datetime.strptime(str(self.start), '%Y-%m-%d %H:%M:%S').date() + timedelta(hours=self.duration),
                                'start': datetime.strptime(str(self.start), '%Y-%m-%d %H:%M:%S').date(),
                                })
            # ~ values2.update({'duration': self.duration})
            _logger.error(f"Secund{values2=}")
            # ~ _logger.error(f"{val=}")
            return values2
            
#TODO: is_calendar for contracts that should have calendar_id so that you can show and not show contracts in calendar


class ContractLineExtend(models.Model):
    _inherit = 'contract.line'
    
    location = fields.Char(string="Location")


