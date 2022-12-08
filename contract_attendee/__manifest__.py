{
    "name": "Contract attendee",
    "summary": "Contract attendee",
    "version": "14.0.1.0.0",
    "category": "Contract",
    "website": "https://vertel.se",
    "author": "Vertel AB",
    "maintainers": ["Vertelab"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'contract_calendar',
        'calendar_attendee_planning',
    ],
    "auto_install": True,
    "data": [
        'views/calendar_view.xml'
    ],
}
