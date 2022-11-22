import datetime
import logging

from odoo import models, fields, api, _
from datetime import datetime, timedelta 


_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = "contract.contract"
    _inherits = {'calendar.event': 'event_id'}
    event_id = fields.Many2one(comodel_name='calendar.event',
                    string='Calendar', auto_join=True, index=True, 
                    ondelete="cascade", required=True)         

    start = fields.Datetime(compute='_inherit_date', readonly=False)
    # skill_ids = fields.Many2many('res.skill', string='Skills')
    # allergy_ids = fields.Many2many('res.allergy', string='Allergies')     

    @api.depends("date_start")           
    def _inherit_date(self):
        self.start = self.date_start

    @api.onchange("start_date")
    def _inherit_stop_date(self):
        self.stop_date = self.start_date

    @api.model_create_multi
    def create(self, vals_list):
        contracts = self.env["contract.contract"]
        for vals in vals_list:
            _logger.warning(f"vals get start {vals.get('start')}")
            if vals['allday'] == True:
                event = self.env['calendar.event'].create({
                    'name': vals.get('name',),
                    'start_date': vals.get('start_date', ),
                    'stop_date': vals.get('stop_date', ),
                    'allday': vals.get('allday', True),
                })
            elif vals['allday'] == False:
                event = self.env['calendar.event'].create({
                    'name': vals.get('name',),
                    'start': vals.get('start', ),
                    'stop': datetime.strptime(vals.get('start', ), '%Y-%m-%d %H:%M:%S') + timedelta(hours=vals.get('duration')),
                    # 'start': datetime(2022, 11, 21, 6, 0),
                    # 'stop': datetime(2022, 11, 21, 7, 0),
                    'duration': vals.get('duration',),
                })
                vals["stop"] = event.stop
            
            vals["event_id"] = event.id

            _logger.warning(f"contract.contract create vals {vals}") 
            contract = super(Contract, self.with_context()).create(vals)
            event.contract_id = contract.id
            contracts += contract
        self.clear_caches()
        return contracts

    def write(self, values):
        interesting_keys = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
        prelim_dict = {}
        for key in interesting_keys:
            day = values[key] if key in values.keys() else False
            if day:
                prelim_dict[key] = day
                values.pop(key)
        if prelim_dict:
            super().write(prelim_dict)
            # _logger.warning(f"PRINT prelim {prelim_dict}")
        res = super().write(values)
        # _logger.warning(f"PRINT values {values}")
        for contract in self:
            # _logger.warning(f"first loop {contract}")
            for event in contract.event_id.recurrence_id.calendar_event_ids:
                # _logger.warning(f"second loop {event}")
                event.write({'contract_id': contract.id})

        return res

#TODO: is_calendar for contracts that should have calendar_id so that you can show and not show contracts in calendar

