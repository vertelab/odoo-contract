import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class BookingResource(models.Model):
    _description = "Agreement Property"
    _inherit = 'booking.resource'
    
    #agreement_ids = fields.One2many('agreement', inverse='booking_resource_id')
    
    def action_agreement(self):
        type_id = self.env.ref('agreement_legal.agreement_type_contract').id
        return {
            'name': _("Agreements"),
            'type': 'ir.actions.act_window',
            'res_model':'agreement',
            'view_mode': 'kanban,list,form',
            'domain': [('booking_resource_id', '=', self.id)],
            'context': {
                'default_booking_type_id': self.booking_type_ids[0].id if self.booking_type_ids else False,
                'default_booking_resource_id': self.id,
                'default_name':self.name,
                'default_agreement_type_id':type_id,
            }
        }


class Agreement(models.Model):
    _inherit = 'agreement'
    
    booking_type_id = fields.Many2one(
            'booking.type',
            string="Booking Type",
            required=False,
            default=None,
            )

    booking_resource_id = fields.Many2one(
            'booking.resource',
            string="Booking Resource",
            required=False,
            default=None,
            )
            
    second_hand_booking_resource_id = fields.Many2one(
            'booking.resource',
            string="Second Hand Booking Resource",
            required=False,
            default=None,
            readonly=True
            )
    
    calender_event_agreement_booking_id = fields.Many2one('calendar.event',help="used to make resource unavailable during agreement")
    
    def get_calendar_values(self):
        vals = {
                'name':f'[{self.name}] Long term booking-{self.contract_id.partner_id.name}-{self.booking_resource_id.name}',
                'start':self.start_date,
                'stop':self.end_date,
                'partner_ids': [(4, self.partner_id.id)],
                'partner_id':self.partner_id.id,
                'booking_type_id':self.booking_type_id.id,
                'booking_status':'booked',
                'resource_ids':[(4, self.booking_resource_id.id)],
        }
        return vals
    
    
    def make_resource_unavailable(self):
        _logger.warning("make_resource_unavailable"*100)
        for record in self:
            _logger.warning(f"{record=}")
            #Create calender event for the duration of the agreement so the resource is unavailable.
            #Create a second resource with an empty schedule so that we can make it available and capture the fact that it has been booked in second hand.
            if record.booking_resource_id:
                _logger.warning(f"{record.booking_resource_id=}")
                existing_events = self.env['calendar.event'].search([
                    ('resource_ids', 'in', self.booking_resource_id.id),
                    ('start', '<', self.end_date),
                    ('stop', '>', self.start_date),
                    ('booking_status', '=', 'booked'),
                ])
                _logger.warning(f"{existing_events=}")
                if existing_events:
                    error_msg = "Overlapping bookings:\n"
                    for event in existing_events:
                        _name = event.name
                        _start = event.start
                        _stop = event.stop
                        _booking_type = event.booking_type_id.name if event.booking_type_id else "N/A"
                        error_msg += f"Event: {_name}, Start: {_start}, Stop: {_stop}, from booking type: {_booking_type}\n"
                    raise UserError(error_msg)
                _logger.warning("before create")
                
                calendar_vals = self.get_calendar_values()
                _logger.warning(f"{calendar_vals}")
                
                self.calender_event_agreement_booking_id = self.env['calendar.event'].create(calendar_vals)
                _logger.warning("after create")
                _logger.warning(f"{self.calender_event_agreement_booking_id=}")
                
                #return self.calender_event_agreement_booking_id
            record.create_second_hand_booking_resource()
                
    def create_second_hand_booking_resource(self):
        for record in self:
            if record.booking_resource_id and not record.second_hand_booking_resource_id:
               record.second_hand_booking_resource_id = self.booking_resource_id.copy()
               record.second_hand_booking_resource_id.name = f"{self.booking_resource_id.name} - open booking"
               record.second_hand_booking_resource_id.resource_calendar_id = self.env['resource.calendar'].create({'name':record.second_hand_booking_resource_id.name}) 
               record.second_hand_booking_resource_id.resource_calendar_id.attendance_ids = False
               

 



