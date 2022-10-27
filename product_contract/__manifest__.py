# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Contract - product",
    "summary": "Adds contract functionality to a product",
    "version": "14.0.1.0.0",
    "development_status": "Beta",
    "category": "Sale",
    "website": "https://vertel.se",
    "author": "Vertel AB",
    "maintainers": ["Vertelab"],
    "license": "AGPL-3",
    "application": False,
    "auto-install": False,
    "installable": True,
    "depends": [
        "contract",
        "product",
        "sale",
    ],
    "data": [
        "views/product_view.xml",
        "views/contract.xml",
    ],
}
