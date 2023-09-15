import logging, datetime
from odoo import api, fields, models
from odoo.tools.translate import _
from collections import Iterable
import json
from datetime import date
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ContractContract(models.Model):
    _name = "contract.contract"
    _inherit = [
        'contract.contract',
        'mail.render.mixin'
    ]
    """
    Overrides function in contract.contract, 
    so that we can use jinja when you create an invoice from a contract
    """

    def _prepare_recurring_invoices_values(self, date_ref=False):
        _logger.warning('_prepare_recurring_invoices_values running... date_ref = %s' % date_ref)
        invoices_values = super()._prepare_recurring_invoices_values(date_ref)
        for inv in invoices_values:
            inv['narration'] = self.note
            _logger.warning(repr(inv['narration']))
            inv['narration'] = self._render_template_jinja(

                inv['narration'],
                "contract.contract", 
                [self.id]
            )
            tp=str(inv['narration']).split("'",1)
            tp=tp[1][:-2]
            tp=tp.replace('\\n', '\n')
            inv['narration']=tp
            _logger.warning(repr(inv['narration']))
                
                
            n = 0
            for line in inv['invoice_line_ids']:
                line[2]['name'] = self._render_template_jinja(

                    line[2]['name'],
                    "contract.line", 
                    [self.contract_line_ids[n].id]
                )
                tp=str(line[2]['name']).split("'",1)
                tp=tp[1][:-2]
                line[2]['name']=tp
                n = n+1
                # ~ _logger.warning(line[2]['name'])

        invoices_values_json=""
        
        try:

            invoices_values_json = json.dumps(invoices_values, cls=DateEncoder)
            # ~ _logger.warning(f"{invoices_values_json=}")
        
        except TypeError:
            
            raise UserError('At least one of the values in the form can not be parsed with '\
                            'json.stringify check "website_quote_jinja_description" for more')

        """
        In this function call we are giving it a string, a module and a list of ids. The thing that needs commenting is the 
        module. The module that this funcion "should" get is the module that the string is a part of. We are not doing 
        that, we are lying to the function by giving it contract.line, instead of what it would be otherwise, contract.contract.
        contract.line is a list that is inside of contract.contract, and that list contains most of the things that you would
        want to reach through Jinja in this situation. That is the reason why we are doing this, because now, most of the time 
        you need to write alot less to reach the data that you need.
        """
        
        for line_id in self.contract_line_fixed_ids.ids:
            new_invoices_values_json = self._render_template_jinja(

                invoices_values_json,
                "contract.line", 
                [line_id]
                )
            _logger.warning(f"{new_invoices_values_json=}")
            # ~ _logger.warning(f"{new_invoices_values_json[line_id][0]=}")
            # ~ _logger.warning(f"{new_invoices_values_json[line_id][1][2]=}")
            d1_eval = eval(new_invoices_values_json[line_id].replace('false','False').replace('true','True'))
            # ~ d1_eval = eval(new_invoices_values_json[line_id])
            # ~ _logger.warning(f"{d1_eval[0]['invoice_line_ids']=}")
            # ~ _logger.warning(f"{d1_eval[0]['invoice_line_ids'][n][2]['contract_line_id']=}")
            for n in self.contract_line_fixed_ids.ids:
                _logger.warning(n)
                _logger.warning(n)
                _logger.warning(n)
                _logger.warning(n)
                # ~ _logger.warning(f"{d1_eval[0]['invoice_line_ids'][n][2]['contract_line_id']=}")
                _logger.warning(type(line_id))
                _logger.warning(line_id)
                # ~ if line_id = d1_eval[0]['invoice_line_ids'][n][2]['contract_line_id']:
                    # ~ invoices_values = d1_eval[0]['invoice_line_ids'][n][2]['contract_line_id'] + invoices_values
                    
                
            _logger.warning(f"{d1_eval=}")
            _logger.warning(f"{invoices_values=}")
            # ~ invoices_values[0]['invoice_line_ids'][n][2].update(d1_eval[0]['invoice_line_ids'][n][2])
            _logger.warning(f"{invoices_values=}")
            
            # ~ _logger.warning(f"{new_invoices_values_json['invoice_filter_type_domain']}")
            # ~ _logger.warning(f"In for, with line_id {line_id} result:{new_invoices_values_json['invoice_line_ids']=}")
        # ~ invoices_note_json = self._render_template_jinja(

            # ~ invoices_values_json,
            # ~ "contract.contract", 
            # ~ [self.id]
            # ~ )
        
        """
        Jinja believes that we have given it uniques strings for each of the ids connected to the module, but we are using this function
        differently, so we are sending the same string for all of them, since that string contains all the information  that we need.
        This makes Jinja return multiples of the same string, for every id, we only need one of them. 
        That is the reason that we put "0" bellow.
        """
        try:
            # ~ _logger.warning(f"{invoices_values_json=}")
            invoices_values_json = invoices_values_json[self.contract_line_fixed_ids.ids[0]]  

            invoices_values = json.loads(
            invoices_values_json, 
            object_hook=DateEncoder.date_decoder
            )     
        
        except:

            _logger.error("invoice values was empty")
        

        _logger.warning(f"{invoices_values=}")
        # ~ _logger.warning(f"{invoices_note_json=}")
        # ~ invoices_values[0]['narration']=invoices_note_json['note']
        return invoices_values
    
class DateEncoder(json.JSONEncoder):


    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()  
        return super().default(obj)

    @staticmethod
    def date_decoder(dct):
        for key, value in dct.items():
            if isinstance(value, str) and value.startswith("DATE:"):
                date_string = value.split("DATE:")[1]
                dct[key] = datetime.datetime.strptime(date_string, "%Y-%m-%d").date()

        return dct
    
    

"""
JSON stringify does not work on the original date format, 
so we convert it to a date format that works for json stringify, 
and then convers it back
"""

