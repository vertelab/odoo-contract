# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2023- Vertel AB (<https://vertel.se>).
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Variable quantity in contract recurrent invoicing: Analytics Account Formula',
    'version': '14.0.0.0.0',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'Adds a special Formula (quantity) which uses Analytics Account',
    'category': 'Sales',
    'description': """
        This module adds a new Formula (quantity) for variable quantity in contract.
        This formula is intended to be used when one wants to use a contract,
        to onward bill a invoice.
        
        This Formula will look in all posted in-invoices for any line that refers to:
        the same produkt as in contract line,
        the same analytics account as in the contract line,
        that has not been invoiced by this formula before,
        and that is from before the contract lines end date.

        To know if a invoice line has been invoiced already,
        a link between invoice lines and contracts as been created.
        This field will be set when the formula fetches the quantity from a invoice line.
        This is to ensure a invoice line's quantity is only fetched once,
        and thus not billed onwards more then once.
    """,
    #'sequence': '1',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-contract/contract-cariable-quantity-analytics-account',
    'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-contract',
    # Any module necessary for this one to work correctly
    
    "application": False,
    "installable": True,
    'depends': ['contract_variable_quantity','account' ],
    "auto_install": True,
    "data": [
        "views/account_move_view.xml",
        "data/contract_line_qty_formula.xml",
    ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
