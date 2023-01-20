{
    'name': 'Contract: Product Contract Timesheet',
    'version': '14.0.0.0.0',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'Glue module between product_contract and contract_timesheet.',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'description': """
    When a project has been generated at contract creation, connect the created project to the sale order.
    """,
    #'sequence': '1',
    'author': 'Vertel AB',
    # 'website': 'https://vertel.se/apps/odoo-contract/product_contract',
    # 'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-contract',
    # Any module necessary for this one to work correctly
    "application": False,
    "auto-install": True,
    "installable": True,
    "depends": [
        "product_contract",
        "contract_timesheet"
    ],
    "data": [
    ],
}