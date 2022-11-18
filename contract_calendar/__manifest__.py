# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Contract - Calendar",
    "summary": "Adds calendar to a contract",
    "version": "14.0.1.0.0",
    "development_status": "Beta",
    "category": "Marketing",
    "website": "https://vertel.se",
    "author": "Vertel AB",
    "maintainers": ["Vertelab"],
    "license": "AGPL-3",
    "application": False,
    "auto-install": False,
    "installable": True,
    "depends": [
        "contract",
        "calendar",
        'contract_cleaner',
        'contract_allergic',
    ],
    "data": [
        "views/contract.xml",
        "views/calendar_view.xml",
    ],
}
