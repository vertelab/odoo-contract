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


{
    'name': 'Product Contract',
    'version': '1.0',
    'category': 'Sale',
    'description': """
Product that creates contract
=============================

* Tie a contract template to a product and a new contract will be generated upon sale.
* Contract templates have recurring invoices enabled, enabling the sale of subscriptions.

Subscriptions:

* When selling several products of this type, the amount on contract-products will be increased
* Date of next invoice are calculated as next invoice repetion + 1. Using the invoice created
  from the sale order as the first.
* Create reccuring invoices using a wizard (or cron)



    """,
    'author': 'Vertel AB',
    'website': 'http://www.vertel.se',
    'depends': ['account_analytic_analysis', 'sale'],
    'data': [
        'product_contract_view.xml',
        ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
