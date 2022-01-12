# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Agreement - Property integration",
    "summary": "Inherit variables from property into agreement",
    "version": "14.0.1.0.0",
    "development_status": "Beta",
    "category": "Marketing",
    "website": "TODO",
    "author": "Emanuel Bergsten",
    "maintainers": ["Vertelab"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "property_mgmt",
        "agreement_legal",
    ],
    "data": [
        "views/agreement.xml",
    ],
}
