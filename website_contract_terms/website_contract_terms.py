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


class sale_order(models.Model):
    _inherit = "sale.order"

    # description = fields.Text(related='project_id.analytic_account_id.description', string='Terms')
    # terms_page = fields.Text(related='project_id.analytic_account_id.terms_page', string='Terms Page')


class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    terms_page = fields.Many2one(comodel_name='ir.model.data', domain=[('module', '=', 'website')])
    # terms_page = fields.Many2one(comodel_name='ir.ui.view', domain=[('type', '=', 'QWeb')])
