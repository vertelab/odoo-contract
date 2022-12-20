{
    "name": "Contract Timesheet",
    "summary": "Contract timesheet",
    "version": "14.0.1.0.0",
    "category": "Contract",
    "website": "https://vertel.se",
    "author": "Vertel AB",
    "maintainers": ["Vertelab"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "contract",
        "hr_timesheet_sheet",
        "project"
    ],
    "auto_install": True,
    "data": [
        "data/project_views.xml",
        "data/contract_views.xml",
    ],
}
