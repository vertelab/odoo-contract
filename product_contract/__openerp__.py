# -*- coding: utf-8 -*-
##############################################################################
#
#   www.vertel.se
#
##############################################################################

{
    'name': 'Product Contract',
    'version': '1.0',
    'category': 'Sale',
    'description': """
Product that creates contract
=============================

* Tie a contract template to a product and a new contract will be generated upon sale.
* Contract templates have recurring invoices enabled, enabling the sale of subscriptions.

Subscriptions:

* When selling several products of this type, the amount on contract-products will be increased
* Date of next invoice are calculated as next invoice repetion + 1. Using the invoice created
  from the sale order as the first.
* Create reccuring invoices using a wizard (or cron)



    """,
    'author': 'Vertel AB',
    'website': 'http://www.vertel.se',
    'depends': ['account_analytic_analysis', 'sale'],
    'data': [
        'product_contract_view.xml',
        ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
