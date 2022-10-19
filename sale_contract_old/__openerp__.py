# -*- coding: utf-8 -*-
##############################################################################
#
#   www.vertel.se
#
##############################################################################

{
    'name': 'Sale Contract',
    'version': '1.0',
    'category': 'Sale',
    'description': """
Manage your contract.
=========================================================================================================
    """,
    'author': 'Vertel AB',
    'license': 'AGPL-3',
    'website': 'http://www.vertel.se',
    'depends': ['account_analytic_analysis', 'website_quote','website_contract_terms'],
    'data': [
        'views/sale_contract.xml',
        # 'security/ir.model.access.csv',
        # 'security/sale_contract_security.xml',
        'wizard/contract_template.xml',
       ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
