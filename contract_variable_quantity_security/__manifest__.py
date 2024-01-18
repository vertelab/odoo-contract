# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Contract Variable Quantity Security',
    'version': '14.0.0.0.0',
    'summary': 'Adds security layer to Contract',
    'category': 'Sales',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-contract/contract_security',
    'license': 'AGPL-3',
    'maintainer': 'Vertel AB',
    "auto_install": True,
    "installable": True,
    'depends': ['contract_variable_quantity'],
    "data": [
        'security/ir.model.access.csv',

        'views/menu.xml',
    ],
}
