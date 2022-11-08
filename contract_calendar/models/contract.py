import datetime
import logging

from odoo import models, fields, api, _
from datetime import datetime


_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = "contract.contract"
    _inherits = {'calendar.event': 'event_id'}
    event_id = fields.Many2one(comodel_name='calendar.event',
                    string='Calendar', auto_join=True, index=True, 
                    ondelete="cascade", required=True)         

    start = fields.Datetime(compute='_inherit_date', readonly=False)     

    @api.depends("date_start")           
    def _inherit_date(self):
        self.start = self.date_start

    @api.model_create_multi
    def create(self, vals_list):
        contracts = self.env["contract.contract"]
        for vals in vals_list:
            event = self.env['calendar.event'].create({
                'name': vals.get('name',),
                'start_date': vals.get('date_start', fields.Date.today()),
                'stop_date': vals.get('date_end', 'date_start'), 
                'duration': vals.get('duration', 1), 
            })
            vals["event_id"] = event.id
            # _logger.warning(f"contract.contract BAPIDI {vals}")
            contract = super(Contract, self.with_context()).create(vals)
            event.contract_id = contract.id
            contracts += contract
        self.clear_caches()
        return contracts

    def write(self, values):
        res = super(Contract, self).write(values)
        return res

#TODO: is_calendar for contracts that should have calendar_id so that you can show and not show contracts in calendar

