# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015- Vertel AB (<http://www.vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
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


from odoo import api, models, fields, _
import logging
_logger = logging.getLogger(__name__)


class product_template(models.Model):
    _inherit = 'product.template'
    
    is_hour_bank = fields.Boolean(string='Is Hour Bank')

    

class product_product(models.Model):
    _inherit = 'product.product'
    
    hour_bank = fields.Float(string='Hour Bank',help="Number of hours for each invoicing period usually month or quater")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
