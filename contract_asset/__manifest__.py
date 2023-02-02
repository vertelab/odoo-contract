{
    "name": "Contract: Contract Assets",
    "summary": "Manage Contract Assets",
    "version": "14.0.1.0.0",
    "category": "Contract",
    "website": "https://vertel.se",
    "author": "Vertel AB",
    "maintainers": ["Vertelab"],
    'images': ['static/description/banner.png'], # 560x280 px.
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    'depends': ['contract','account_asset_management', ],
    "auto_install": False,
    "data": [
        'views/contract_view.xml'
    ],
}
