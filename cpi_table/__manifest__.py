# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Consumer Price Index - Table",
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
        "base",
        "agreement_legal",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/consumer_price_index.xml",
    ],
}
