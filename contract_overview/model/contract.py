from odoo import models, fields, api


class Contract(models.Model):
    _inherit = "contract.contract"

    def _qweb_prepare_qcontext(self, view_id, domain):
        values = super()._qweb_prepare_qcontext(view_id, domain)

        contracts = self.search(domain)
        values.update(contracts._plan_prepare_values())

        print(values)
        # values['actions'] = contracts._plan_prepare_actions(values)

        return values

    def _plan_prepare_values(self):
        currency = self.env.company.currency_id
        uom_hour = self.env.ref('uom.product_uom_hour')
        company_uom = self.env.company.timesheet_encode_uom_id
        is_uom_day = company_uom == self.env.ref('uom.product_uom_day')
        billable_types = ['non_billable', 'non_billable_project', 'billable_time', 'non_billable_timesheet', 'billable_fixed']

        values = {
            'contracts': self,
            'currency': currency,
            'timesheet_domain': [('project_id', 'in', self.ids)],
            'profitability_domain': [('project_id', 'in', self.ids)],
            'stat_buttons': self._plan_get_stat_button(),
            'is_uom_day': is_uom_day,
        }

        dashboard_values = {
            'time': dict.fromkeys(billable_types + ['total'], 0.0),
            'rates': dict.fromkeys(billable_types + ['total'], 0.0),
            'profit': {
                'invoiced': 0.0,
                'to_invoice': 0.0,
                'cost': 0.0,
                'total': 0.0,
            }
        }

        values['dashboard'] = dashboard_values

        return values