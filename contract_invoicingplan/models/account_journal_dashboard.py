import json
from datetime import datetime, timedelta

from babel.dates import format_datetime, format_date
from odoo import models, api, _, fields
from odoo.osv import expression
from odoo.release import version
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools.misc import formatLang, format_date as odoo_format_date, get_lang
import random

import ast


class account_journal(models.Model):
    _inherit = "account.journal"

    def _get_open_uninvoiced_stubs_query(self):
        return ('''
            SELECT
                contract.uninvoiced_stubs
            FROM contract_contract contract
            WHERE contract.journal_id = %(journal_id)s
            AND contract.uninvoiced_stubs = True;
        ''', {'journal_id': self.id})

    def _get_open_zero_invoice_stubs_count_query(self):
        return ('''
            SELECT
                contract.contract_invoice_sub_count
            FROM contract_contract contract
            WHERE contract.journal_id = %(journal_id)s
            AND contract.contract_invoice_sub_count = 0;
        ''', {'journal_id': self.id})

    def get_journal_dashboard_datas(self):
        datas = super().get_journal_dashboard_datas()

        number_uninvoiced_stubs = number_zero_invoice_stubs = 0
        sum_uninvoiced_stubs = sum_zero_invoice_stubs = 0.0

        if self.type in ['sale', 'purchase']:
            (query, query_args) = self._get_open_uninvoiced_stubs_query()
            self.env.cr.execute(query, query_args)
            query_results_to_uninvoiced_stubs = self.env.cr.dictfetchall()
            number_uninvoiced_stubs = len(query_results_to_uninvoiced_stubs)

            (query, query_args) = self._get_open_zero_invoice_stubs_count_query()
            self.env.cr.execute(query, query_args)
            query_results_to_zero_invoice_stubs = self.env.cr.dictfetchall()
            number_zero_invoice_stubs = len(query_results_to_zero_invoice_stubs)

        datas.update({
            'number_uninvoiced_stubs': number_uninvoiced_stubs,
            'sum_uninvoiced_stubs': sum_uninvoiced_stubs,
            'number_zero_invoice_stubs': number_zero_invoice_stubs,
            'sum_zero_invoice_stubs': sum_zero_invoice_stubs
        })

        return datas

    def open_uninvoiced_subs_contract_action(self):
        tree_view_id = self.env.ref('contract.contract_contract_tree_view').id

        return {
            'type': 'ir.actions.act_window',
            'name': _('Contracts'),
            'view_mode': 'tree,form',
            'res_model': 'contract.contract',
            'target': 'self',
            'views': [[tree_view_id, 'tree'], [False, 'form']],
            'domain': [('uninvoiced_stubs', '=', True)]
        }

    def open_invoiced_subs_contract_action(self):
        tree_view_id = self.env.ref('contract.contract_contract_tree_view').id

        return {
            'type': 'ir.actions.act_window',
            'name': _('Contracts'),
            'view_mode': 'tree,form',
            'res_model': 'contract.contract',
            'target': 'self',
            'views': [[tree_view_id, 'tree'], [False, 'form']],
            'domain': [('contract_invoice_sub_count', '=', 0)]
        }

