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


class AccountMove(models.Model):
    _inherit = "account.move"

    contract_stub_id = fields.Many2one('contract.invoice.stub', string="Contract Stub")

    contract_id = fields.Many2one('contract.contract', string="Contract")

