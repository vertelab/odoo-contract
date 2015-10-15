# -*- coding: utf-8 -*-
##############################################################################
#
#   www.vertel.se
#
##############################################################################

{
    'name': 'Subscriptions',
    'version': '1.0',
    'category': 'Sale',
    'description': """
Tie a contract template to a product. A new contract will be generated upon sale. Contract templates have recurring invoices activated, enabling the sale of subscriptions.
=========================================================================================================
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
