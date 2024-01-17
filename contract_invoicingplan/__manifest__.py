# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Contract: Contract Monthly Value',
    'version': '14.0.0.0.0',
    'summary': 'Contract Monthly Value',
    'category': 'Sales',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-contract/contract_monthly_value',
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
