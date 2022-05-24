# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Agreement - Calculate",
    "summary": "TODO: Caculate variables from contract and property",
    "version": "14.0.1.0.0",
    "development_status": "Beta",
    "category": "Marketing",
    "website": "https://vertel.se",
    "author": "Vertel AB",
    "maintainers": ["Vertelab"],
    "license": "AGPL-3",
    "application": False,
    "auto-install": True,
    "installable": True,
    "depends": [
        "agreement_contract",
        "agreement_property",
        "contract",
        "uom",
    ],
    "data": [
        "views/agreement.xml",
    ],
}
