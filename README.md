

## Porteringsstatus

18.0 är baseline. 19.0/20.0 visar om p-filen har ett villkor för utgåvan
— inte om grenen finns. Blockerare är `depends` som saknas i 20.0
(kärna + alla 20.0-grenar).

| Modul | Beskrivning | Manifest | p-fil | 19.0 | 20.0 | Blockerare |
|---|---|---|---|---|---|---|
| account_agreement | Account - Extension to be used together with Agreement. | 1.0.0 | 0 | — | — | `agreement_legal` `contract` |
| agreement_base_booking | Connect a booking type and resource to a agreement. | 1.0.0 | 1 | — | ✓ | `agreement_legal` |
| agreement_calculate | Agreement - Calculate. | 1.0.0 | 0 | — | — | `contract` |
| agreement_contract | Agreement - Contract integration. | 1.0.0 | 1 | — | ✓ | `agreement_legal` `contract` |
| agreement_property | Inherit variables from property into agreement. | 1.0.0 | 0 | — | — | `property_mgmt` `property_building` `agreement_legal` |
| contract_aaw | Invoice Alter and Additional Work , AAW. | 1.0.0 | 1 | — | ✓ | `contract_variable_quantity` `project_task_stock` |
| contract_edit_active_lines | This module will let us show the cancel button on active ... | 1.0.0 | 0 | — | — | `contract` |
| contract_invoicingplan | Contract invoicing plan. | 1.0.0 | 3 | — | ✓ | `contract` |
| contract_loan | Contract Loan. | 1.0.0 | 0 | — | — | `account_loan` |
| contract_monthly_value | Will generate monthly value of each contract. | 1.0.0 | 0 | — | — | `contract` |
| contract_recurring_event | Manage your Contract Recurring Event. | 1.1.0 | 0 | — | — | `contract` `contract_termination` |
| contract_variable_qty_hour_bank | Invoice hours exceeding an hour bank. | 1.1.0 | 0 | — | — | `contract_variable_quantity` `product_contract` |
| contract_variable_quantity_analytics_account | Adds a special Formula (quantity) which uses Analytics Ac... | 1.0.0 | 0 | — | — | `contract_variable_quantity` |
| cpi_table | Consumer Price Index - Table. | 1.0.0 | 1 | — | ✓ | `agreement_legal` |
| pricelist_cpi | Adjusts price lists by a consumer price index. | 1.0.0 | 0 | — | — | — |
| product_contract_deprecated | Adds contract functionality to a product. | 1.0.0 | 0 | — | — | — |
| sale_contract | Manage your contract. | 1.1.0 | 0 | — | — | `contract` `product_contract` |
