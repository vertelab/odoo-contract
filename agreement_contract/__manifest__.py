# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Agreement - Contract integration",
    "summary": "TODO: Inherit variables from contract into agreement",
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
        "account",
        "agreement_legal",
        "contract",
        "account_agreement",
        "pricelist_cpi",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/agreement.xml",
    ],
}
