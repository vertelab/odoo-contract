import datetime
import logging

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

# ~ _logger = logging.getLogger(__name__)
_logger = logging.getLogger("\33[1;37m\33[45m"+__name__+"\33[1;37m\33[42m")


class Contract(models.Model):
    _inherit = "contract.contract"
    _inherits = {'calendar.event': 'event_id'}
    event_id = fields.Many2one(comodel_name='calendar.event', string='Calendar')
                    
    # ~ @api.onchange('end_type')
    # ~ def no_set_repitions(self):
        # ~ if self.end_type == "count":
           # ~ raise UserError(_("We only support forever and end date as end types")) 
            
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
                
    # ~ def event_vals(self, "values"):
        # ~ if type(values) == list:
            # ~ values2 = []
            # ~ for val2 in values:
                # ~ values2_dict = {}
                # ~ for key_field in val2:
                    # ~ if key_field in self.env['calendar.event']._fields:
                        # ~ values2_dict[key_field] = val2[key_field]
                # ~ values2.append(values2_dict)
        # ~ else:
            # ~ values2 = {}
            # ~ for key_field in values:
                # ~ if key_field in self.env['calendar.event']._fields:
                    # ~ values2[key_field] = values[key_field]

    @api.model_create_multi
    def create(self, vals_list):
        _logger.error("HEY")
        _logger.warning(f"contract.contract create {vals_list}")
        # ~ contracts = self.env["contract.contract"]
        
        for vals in vals_list:
            event_list = self.event_vals(vals)
            _logger.warning(f"calendar.event event_list {event_list}")
            event_id = self.env['calendar.event'].create(event_list)
        
        # ~ for vals in vals_list:
            # ~ _logger.error("TEST")
            # ~ if not self.env.context.get('from_sale_order') and 'date_end' in vals and vals['date_end'] == False:
                # ~ _logger.warning(f"1"*50)
                # ~ date_end = datetime.strptime(str(vals.get('date_start')),'%Y-%m-%d') + relativedelta(years=5)
                # ~ vals['date_end'] = str(date_end.date())
            # ~ if not self.env.context.get('from_sale_order') and 'allday' in vals and vals['allday'] == True:
                # ~ _logger.warning(f"2"*50)
                # ~ event_list = self.event_vals(vals_list)
                # ~ event_id = self.env['calendar.event'].create(event_list)
                # ~ vals["event_id"] = event_id.id
                # ~ _logger.error(f"{event_id=}")
                # ~ _logger.error(f"{vals=}")
                # ~ event = self.env['calendar.event'].create({
                    # ~ 'name': vals.get('name', ),
                    # ~ 'start_date': vals.get('start_date', ),
                    # ~ 'stop_date': vals.get('stop_date', ),
                    # ~ 'allday': vals.get('allday', True),
                    # ~ 'partner_ids': vals.get('partner_ids', ),
                    # ~ 'active': True,
                # ~ })
            # ~ elif not self.env.context.get('from_sale_order') and 'allday' in vals and vals['allday'] == False:
                # ~ _logger.warning(f"3"*50)
                # ~ event = self.env['calendar.event'].create({
                    # ~ 'name': vals.get('name', ),
                    # ~ 'start': vals.get('start', ),
                    # ~ 'stop': datetime.strptime(vals.get('start', ), '%Y-%m-%d %H:%M:%S') + timedelta(hours=vals.get('duration')),
                    # ~ 'duration': vals.get('duration',),
                    # ~ 'partner_ids': vals.get('partner_ids', ),
                    # ~ 'active': True,
                # ~ })
                
                # ~ event_list = self.event_vals(vals_list)
                # ~ _logger.warning(f"{event_list=}")
                # ~ _logger.warning(f"{vals_list=}")
                # ~ event_id = self.env['calendar.event'].create(event_list)
                # ~ vals["event_id"] = event_id.id
                # ~ _logger.error(f"{event_id=}")
                # ~ _logger.error(f"{vals=}")

            # ~ elif self.env.context.get('from_sale_order'):
                # ~ _logger.warning(f"4"*50)
                # ~ event = self.env['calendar.event'].create({
                    # ~ 'name': vals.get('name', ),
                    # ~ 'start': vals.get('start', ),
                    # ~ 'stop': datetime.strptime(str(vals.get('start', )), '%Y-%m-%d %H:%M:%S') + timedelta(hours=vals.get('duration',1)),
                    # ~ #'duration': 1,
                    # ~ 'partner_ids': [(5, 0, 0)],
                    # ~ 'active': True,
                # ~ })
                # ~ event_list = self.event_vals(vals_list)
                # ~ _logger.warning(f"{event_list=}")
                # ~ _logger.warning(f"{vals_list=}")
                # ~ if len(event_list) > 0:
                # ~ event_id = self.env['calendar.event'].create(event_list)
                # ~ vals.pop('date_order', None)
                # ~ vals["event_id"] = event_id.id
                # ~ _logger.error(f"{event_id=}")
                # ~ _logger.error(f"{vals=}")
            # ~ contract = super(Contract, self.with_context()).create(vals)
            # ~ if vals.get('event_id') and vals['event_id'] != False:
            # ~ self.assign_contract(event_id, vals, contract)
            # ~ contracts += contract
        # ~ self.clear_caches()
        contract = super(Contract, self.with_context()).create(vals_list)
        return contract
    
    def write(self, values):
        _logger.error(f"{values=}")
                
        # ~ values = {
                    # ~ 'name': self.name, 
                    # ~ 'partner_ids': self.partner_ids, 
                    # ~ 'start': self.start, 
                    # ~ 'stop': datetime.strptime(str(self.start), '%Y-%m-%d %H:%M:%S') + timedelta(hours=self.duration),
                    # ~ 'allday': self.allday, 
                    # ~ 'start_date': self.start_date, 
                    # ~ 'stop_date': self.stop_date, 
                    # ~ 'recurrency': self.recurrency,
                    # ~ 'active': True,
                    # ~ 'interval': self.interval, 
                    # ~ 'rrule_type': self.rrule_type, 
                    # ~ 'end_type': self.end_type, 
                    # ~ 'count': self.count, 
                    # ~ 'until': self.until, 
                    # ~ 'recurrence_update': self.recurrence_update, 
                    # ~ 'month_by': self.month_by,
                    # ~ 'weekday': self.weekday, 
                    # ~ 'event_tz': self.event_tz, 
                    # ~ 'day': self.day, 
                    # ~ 'byday': self.byday, 
                    # ~ 'recurrence_id': self.recurrence_id, 
                    # ~ 'follow_recurrence': self.follow_recurrence,
                    # ~ 'active': self.active,
                    # ~ 'mo': self.mo, 
                    # ~ 'tu': self.tu, 
                    # ~ 'we': self.we, 
                    # ~ 'th': self.th, 
                    # ~ 'fr': self.fr, 
                    # ~ 'sa': self.sa, 
                    # ~ 'su': self.su,
                    # ~ }
        # ~ interesting_keys = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
        # ~ interesting_calendar_keys = ['name', 'partner_ids', 'start', 'allday', 'start_date', 'stop_date', 'recurrency',
                                     # ~ 'interval', 'rrule_type', 'end_type', 'count', 'until', 'recurrence_update', 'month_by',
                                     # ~ 'weekday', 'event_tz', 'day', 'byday', 'recurrence_id', 'follow_recurrence','active']
        # ~ prelim_dict = { 'active': True,}
        res = super().write(values)
        # ~ event = self.event_vals(values)
        # ~ event_id = self.env['calendar.event'].write(event)
        # ~ if self.env.context.get('from_sale_order'):
            # ~ _logger.error("sale order, "*10)
            # ~ event = self.event_vals(values)
            # ~ event_id = self.env['calendar.event'].write(event)
        # ~ else:
            # ~ _logger.error(f"{self.event_id.recurrency=}")
            # ~ _logger.error("contract, "*10)
            # ~ _logger.error(f"{values=}")
            # ~ self.event_id.write(values)
            # ~ _logger.error(f"{values=}")
        # ~ res = super().write(values)
        # ~ _logger.error(f"{res=}")
        return res

    def unlink(self,super_unlink=False):
        _logger.error("Hello?")
        if super_unlink == True:    # This prevents self.unlink() from calling itself infinitely when unlink is called within a loop
            res = super().unlink()
            return res
        for record in self: # Delete contracts and all their linked calendar events
            event = record.event_id
            recurrences = self.env["calendar.recurrence"].search([
            ('base_event_id.id', 'in', [e.id for e in self]) ])
            _logger.error(f"{recurrences=}")
            record.unlink(True)
            if event.recurrency == True:
                _logger.error(f"{event=}")
                for event_id in event.recurrence_id.calendar_event_ids:
                    _logger.error(f"{event=}")
                    event_id.unlink()
                    _logger.error(f"{event=}")
                    if recurrences:
                        _logger.error(f"{event=}")
                        event_id = recurrences._select_new_base_event()
                        _logger.error(f"{event=}")
            else:
                event.unlink()
                
    def event_vals(self, values):
        if type(values) == list:
            _logger.error(f"{values=}")
            values2 = []
            for val2 in values:
                values2_dict = {}
                for key_field in val2:
                    if key_field in self.env['calendar.event']._fields:
                        values2_dict[key_field] = val2[key_field]
                values2.append(values2_dict)
            _logger.error(f"{values2=}")
            return values2
        else:
            values2 = {}
            for key_field in values:
                if key_field in self.env['calendar.event']._fields:
                    values2[key_field] = values[key_field]
            _logger.error(f"{values2=}")
            return values2
            
    def assign_contract(self, event, vals, contract):
        relevant_recurrency = self.env['calendar.recurrence'].search([('base_event_id', '=', event.id), 
                                                                      ('mo', '=', event.mo),
                                                                      ('tu', '=', event.tu),
                                                                      ('we', '=', event.we),
                                                                      ('th', '=', event.th),
                                                                      ('fr', '=', event.fr),
                                                                      ('sa', '=', event.sa),
                                                                      ('su', '=', event.su),])
        if 'recurrency' in vals and vals['recurrency'] == True:
            for sub_event in relevant_recurrency.calendar_event_ids:
                sub_event.contract_id = contract.id
                if sub_event.start == relevant_recurrency.dtstart:
                    contract.event_id = sub_event.id
        if 'recurrency' in vals and vals['recurrency'] == False or 'recurrency' not in vals:
            event.contract_id = contract.id

#TODO: is_calendar for contracts that should have calendar_id so that you can show and not show contracts in calendar


class ContractLineExtend(models.Model):
    _inherit = 'contract.line'
    
    location = fields.Char(string="Location")


