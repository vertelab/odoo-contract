# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account - Extension to be used together with Agreement",
    "summary": "TODO: Inherit variables from contract into agreement",
    "version": "14.0.1.0.0",
    "development_status": "Beta",
    "category": "Marketing",
    "website": "TODO",
    "author": "Emanuel Bergsten",
    "maintainers": ["Vertelab"],
    "license": "AGPL-3",
    "application": False,
    "auto-install": True,
    "installable": True,
    "depends": [
        "agreement_legal",
        "account",
        "contract",
    ],
    "data": [
        "views/account_move.xml",
    ],
}
