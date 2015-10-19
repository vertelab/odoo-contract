# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015- Vertel AB (<http://www.vertel.se>).
#
#    This progrupdateam is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

#~ 
#~ 
#~ class sale_order(models.Model):
    #~ _inherit = "sale.order"
#~ 
    #~ # description = fields.Text(related='project_id.analytic_account_id.description', string='Terms')
    #~ # terms_page = fields.Text(related='project_id.analytic_account_id.terms_page', string='Terms Page')
#~ 
#~ 
#~ class account_analytic_account(models.Model):
    #~ _inherit = 'account.analytic.account'
#~ 
    #~ terms_page = fields.Many2one(comodel_name='ir.model.data', domain=[('module', '=', 'website')])
    #~ # terms_page = fields.Many2one(comodel_name='ir.ui.view', domain=[('type', '=', 'QWeb')])

class account_analytic_account(models.Model):
    _name = "account.analytic.account"
    _inherit = "account.analytic.account"

    order_id = fields.One2many(comodel_name='sale.order',inverse_name='project_id')
    
    @api.onchange('partner_id')
    def sale_onchange_incoice_on_timesheets(self):
        categ_wtime = self.env.ref('product.uom_categ_wtime')  # Working time-type
        service_uom = [c.id for c in self.env['product.uom'].search([('category_id', '=', categ_wtime.id)])]
        service=self.env['product.product'].search([('type', '=', 'service'), ('uom_id', 'in', service_uom)])
        __logger.warn('Service products %s  in %s ' % (service,service in self.env['product.product'].search([])))
        
        raise Warning('Service products %s  in %s ' % (service,service in self.env['product.product'].search([])))
        if self.order_id:
            categ_wtime = self.env.ref('product.uom_categ_wtime')  # Working time-type
            service_uom = [c.id for c in self.env['product.uom'].search([('category_id', '=', categ_wtime.id)])]  # All uom of working time type
            service_products = [p.id for p in self.env['product.product'].search([('type', '=', 'service'), ('uom_id', 'in', service_uom)])]
            other_products = [p.id for p in self.env['product.product'].search([]) if p.id not in service_products]
            service=self.env['product.product'].search([('type', '=', 'service'), ('uom_id', 'in', service_uom)])
            raise Warning('Service products %s  in %s ' % (service,service in self.env['product.product'].search([])))
            if self.fix_price_invoices:
                self.fix_price_invoices = sum([l.price_subtotal for l in order.order_line if l.product_id.id in other_products])
            if self.invoice_on_timesheets:
                self.use_timesheets = True
                self.hours_qtt_est = sum([l.price_subtotal for l in order.order_line if l.product_id.id in service_products])
                self.to_invoice = self.env.ref('hr_timesheet_invoice.timesheet_invoice_factor1')
            if not self.invoice_on_timesheets:
                self.to_invoice = False
            

    #~ @api.onchange('template_id')
    #~ def sale_on_change_template(self):
        #~ if self.order_id:
            #~ categ_wtime = self.env.ref('product.uom_categ_wtime')  # Working time-type
            #~ service_uom = [c.id for c in self.env['product.uom'].search([('category_id', '=', categ_wtime.id)])]  # All uom of working time type
            #~ service_products = [p.id for p in self.env['product.product'].search([('type', '=', 'service'), ('uom_id', 'in', service_uom)])]
            #~ other_products = [p.id for p in self.env['product.product'].search([]) if p.id not in service_products]
            #~ service=self.env['product.product'].search([('type', '=', 'service'), ('uom_id', 'in', service_uom)])
            #~ raise Warning('Service products %s  in %s ' % (service,service in self.env['product.product'].search([])))
            #~ 
            #~ res = super(account_analytic_account, self).on_change_template(self.env.cr, self.env.uid, [self.id], self.template_id, date_start=self.date_start, context=self.env.context)
            #~ if not res['value'].get('amount_max'):
                #~ res['value']['amount_max'] = sum([l.price_subtotal for l in order.order_line if l.product_id.id in other_products])
            #~ if not res['value'].get('hours_qtt_est'):
                #~ res['value']['hours_qtt_est'] = sum([l.price_subtotal for l in order.order_line if l.product_id.id in service_products])
            #~ self.write(res['value'])
            
            #~ 
    #~ def on_change_template(self, cr, uid, ids, template_id, date_start=False, context=None):
        #~ if not template_id:
            #~ return {}
        #~ res = super(account_analytic_account, self).on_change_template(cr, uid, ids, template_id, date_start=date_start, context=context)
#~ 
        #~ template = self.browse(cr, uid, template_id, context=context)
        #~ 
        #~ if not ids:
            #~ res['value']['fix_price_invoices'] = template.fix_price_invoices
            #~ res['value']['amount_max'] = template.amount_max
        #~ if not ids:
            #~ res['value']['invoice_on_timesheets'] = template.invoice_on_timesheets
            #~ res['value']['hours_qtt_est'] = template.hours_qtt_est
        #~ 
        #~ if template.to_invoice.id:
            #~ res['value']['to_invoice'] = template.to_invoice.id
        #~ if template.pricelist_id.id:
            #~ res['value']['pricelist_id'] = template.pricelist_id.id
        #~ if not ids:
            #~ invoice_line_ids = []
            #~ for x in template.recurring_invoice_line_ids:
                #~ invoice_line_ids.append((0, 0, {
                    #~ 'product_id': x.product_id.id,
                    #~ 'uom_id': x.uom_id.id,
                    #~ 'name': x.name,
                    #~ 'quantity': x.quantity,
                    #~ 'price_unit': x.price_unit,
                    #~ 'analytic_account_id': x.analytic_account_id and x.analytic_account_id.id or False,
                #~ }))
            #~ res['value']['recurring_invoices'] = template.recurring_invoices
            #~ res['value']['recurring_interval'] = template.recurring_interval
            #~ res['value']['recurring_rule_type'] = template.recurring_rule_type
            #~ res['value']['recurring_invoice_line_ids'] = invoice_line_ids
        #~ return res
