# -*- coding: utf-8 -*-
##############################################################################
#
#   www.vertel.se
#
##############################################################################

{
    'name': 'Prenumerations',
    'version': '1.0',
    'category': 'Sale',
    'description': """
Sell prenumerations.
=========================================================================================================
    """,
    'author': 'Vertel AB',
    'website': 'http://www.vertel.se',
    'depends': ['account_analytic_analysis', 'website_sale'],
    'data': [
        'product_contract_view.xml',
        ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
