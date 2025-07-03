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
    'name': 'Contract: Invoice Alter and Additional Work Tasks',
    'version': '1.0',
    'summary': 'Invoice Alter and Additional Work , AAW',
    'description': """
        Invoice AAW Tasks.
    """,
    'category': 'Sales',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-contract/contract_aaw',
    'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'maintainer': 'Vertel AB',
    "application": False,
    "auto-install": False,
    "installable": True,
    'depends': [
        'project', 'account', 'contract_variable_quantity', 'contract_invoicingplan', 'hr_timesheet',
        'hr', 'sale_timesheet', 'project_task_stock', 'sale', 'sign_project_task'
    ],
    "data": [
        'views/contract_contract_view.xml',
        'views/contract_template_view.xml',
        'views/project_portal_project_task_templates.xml',
        'views/project_task_view.xml',
        'views/project_project_view.xml',
        'views/hr_timesheet_views.xml',
    ],
}
