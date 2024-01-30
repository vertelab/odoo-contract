# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2024- Vertel AB (<https://vertel.se>).
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

# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Contract: Contract Monthly Value',
    'version': '14.0.0.0.0',
    'summary': 'Contract invoicing plan',
    'description': """
    Create plan using stubbs for invoicing.
    """,
    'category': 'Sales',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-contract/contract_invoicingplan',
    'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'maintainer': 'Vertel AB',
    "application": False,
    "auto-install": False,
    "installable": True,
    'depends': ['contract', 'account', 'account_period'],
    "data": [
        'security/ir.model.access.csv',
        'views/contract_view.xml',
        'views/account_move.xml',
        'views/contract_invoice_sub_view.xml',
        'views/account_journal_dashboard.xml',
        'data/ir_cron.xml',
    ],
}
