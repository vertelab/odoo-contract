# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Contract: Overview',
    'version': '14.0.0.0.0',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'Adds stuff to the Contract view',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-contract/contract_overview',
    'license': 'AGPL-3',
    'maintainer': 'Vertel AB',
    "application": False,
    "auto-install": False,
    "installable": True,
    'depends': ['sale', 'contract'],
    "data": [
        'views/contract_view.xml',
    ],
}
