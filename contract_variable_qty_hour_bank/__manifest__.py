# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#BORROWED MODULE FROM OCA
{
    "name": "Contract Variable Qty Hour Bank",
    "summary": "Invoice hours exceeding an hour bank ",
    "version": "14.0.0.0.0",
    "category": "Contract Management",
    "website": "https://vertel.se/apps/contract_variable_qty_hour_bank",
    "author": "Vertel AB",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["contract_variable_quantity", "hr_timesheet",'product','product_contract'],
    "data": [
            "data/contract_line_qty_formula_data.xml",
            "views/product_view.xml",
            "views/contract_view.xml",
            ],
}
