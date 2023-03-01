import datetime
import logging

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = "contract.contract"
    _inherits = {'calendar.event': 'event_id'}
    event_id = fields.Many2one(comodel_name='calendar.event',
                    string='Calendar', auto_join=True, index=True,
                    required=True)

    # , default=datetime.now().replace(hour=7, minute=0, second=0)
    start = fields.Datetime(related='event_id.start', readonly=False)

    # skill_ids = fields.Many2many('res.skill', string='Skills')
    # allergy_ids = fields.Many2many('res.allergy', string='Allergies')

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
        _logger.warning(f"contract.contract create {vals_list}")
        contracts = self.env["contract.contract"]
        for vals in vals_list:
            if not self.env.context.get('from_sale_order') and 'date_end' in vals and vals['date_end'] == False:
                date_end = datetime.strptime(str(vals.get('date_start')),'%Y-%m-%d') + relativedelta(years=5)
                vals['date_end'] = str(date_end.date())
            # _logger.warning(f"CONTRACT CONTRACT CREATE {vals}")
            if not self.env.context.get('from_sale_order') and 'allday' in vals and vals['allday'] == True:
                # _logger.warning("contract contract inside first if")
                event = self.env['calendar.event'].create({
                    'name': vals.get('name', ),
                    'start_date': vals.get('start_date', ),
                    'stop_date': vals.get('stop_date', ),
                    'allday': vals.get('allday', True),
                    'partner_ids': vals.get('partner_ids', ),
                })
                vals["event_id"] = event.id
            elif not self.env.context.get('from_sale_order') and 'allday' in vals and vals['allday'] == False:
                # _logger.warning("contract contract inside second if")
                event = self.env['calendar.event'].create({
                    'name': vals.get('name', ),
                    'start': vals.get('start', ),
                    'stop': datetime.strptime(vals.get('start', ), '%Y-%m-%d %H:%M:%S') + timedelta(hours=vals.get('duration')),
                    'duration': vals.get('duration',),
                    'partner_ids': vals.get('partner_ids', ),
                })
                vals["event_id"] = event.id
                vals["stop"] = event.stop
            elif self.env.context.get('from_sale_order'):
                event = self.env['calendar.event'].create({
                    'name': vals.get('name', ),
                    'start': vals.get('start', ),
                    'stop': datetime.strptime(str(vals.get('stop', )), '%Y-%m-%d %H:%M:%S') + timedelta(hours=1),
                    'duration': 1,
                    'partner_ids': [(5, 0, 0)],
                    # 'partner_ids': [(6, 0, [vals.get('partner_id', )])],
                })
                vals.pop('date_order', None)
                vals["event_id"] = event.id
                vals["stop"] = event.stop


            # _logger.warning(f"VALS STOP {vals['stop']}")
            # _logger.warning(f"contract before create vals {vals}")
            # _logger.warning("contract right before create")
            # _logger.warning(f"contract.contract create vals {vals}")
            contract = super(Contract, self.with_context()).create(vals)

            if not self.env.context.get('from_sale_order') and vals.get('event_id') and vals['event_id'] != False:
                # _logger.warning("contract contract inside third if")

                relevant_recurrency = self.env['calendar.recurrence'].search([('base_event_id', '=', event.id)])
                if 'recurrency' in vals and vals['recurrency'] == True:
                    # _logger.warning(f"{event.id} {event.recurrence_id} {event.recurrence_id.calendar_event_ids}")
                    for sub_event in relevant_recurrency.calendar_event_ids:
                        sub_event.contract_id = contract.id
                        if sub_event.start == relevant_recurrency.dtstart:
                            contract.event_id = sub_event.id

            # _logger.warning(f"EVENT CONTRACT APPEND {event.contract_id} {contract.id} ")

            contracts += contract

        # if not self.env.context.get('from_sale_order'):
        #     for contract in contracts:
        #         project = self.env['project.project'].create({
        #             'name': contract.name,
        #             'contract_id': contract.id,
        #             'allow_timesheets': True,
        #             'label_tasks': 'Jobs'
        #         })

        self.clear_caches()
        return contracts

    def write(self, values):
        interesting_keys = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
        interesting_calendar_keys = ['name', 'partner_ids', 'start', 'allday', 'start_date', 'stop_date', 'reccurency',
                                     'interval', 'rrule_type', 'end_type', 'count', 'until', ]
        prelim_dict = {}
        contract_vals = {}
        for key in interesting_keys:
            day = values[key] if key in values.keys() else False
            if day:
                contract_vals[key] = day
                prelim_dict[key] = day
        if prelim_dict:
            super().write(prelim_dict)
            # _logger.warning(f"PRINT prelim {prelim_dict}")
        # values['recurrence_update'] = 'future_events'
        # _logger.warning(f"contract.contract write {values}")
        # _logger.warning(f"self contract.contract: {self} {self.event_id}")
        res = super().write(values)
        _logger.warning(f"contract write {values}")

        for key in interesting_calendar_keys:
            input = values[key] if key in values.keys() else False
            if input:
                contract_vals[key] = input
                if key == 'name':
                    self.project_id.name = input
        contract_vals['recurrence_update'] = 'future_events'
        self.event_id.write(contract_vals)
        # _logger.warning(f"PRINT values {values}")

        # unsure about the code below, dont know why i put it there but cant figure out if its needed
        # for contract in self:
        #     # _logger.warning(f"first loop {contract}")
        #     for event in contract.event_id.recurrence_id.calendar_event_ids:
        #         # _logger.warning(f"second loop {event}")
        #         event.write({'contract_id': contract.id})

        return res

    def unlink(self,super_unlink=False):
        if super_unlink == True:    # This prevents self.unlink() from calling itself infinitely when unlink is called within a loop
            res = super().unlink()
            return res

        for record in self: # Delete contracts and all their linked calendar events
            event = record.event_id
            record.unlink(True)

            if event.recurrency == True:
                for event_id in event.recurrence_id.calendar_event_ids:
                    event_id.unlink()
            else:
                event.unlink()


#TODO: is_calendar for contracts that should have calendar_id so that you can show and not show contracts in calendar

