{
    'name': 'Sale Contract',
    'version': '14.0.0.1',
    'category': 'Sale',
    'description': """Manage your contract.""",
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['contract', 'sale', 'calendar'],
    'data': [
        "views/sale_view.xml",
        "views/contract_view.xml",
        "views/calendar_view.xml",
    ],
    'installable': True,
}
