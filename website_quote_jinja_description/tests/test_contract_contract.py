from odoo.tests.common import SavepointCase,Form
from datetime import date
import unittest
import logging, datetime
from odoo import api, fields, models
from odoo.tools.translate import _
from collections import Iterable
import json
from datetime import date
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
    
# This requires demo data
class TestContractContract(SavepointCase):
             
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        
        cls.name="3 chairs a day"
        cls.company_id=cls.env['res.company'].search([('name', '=', 'YourCompany')])
        cls.partner_id=cls.env['res.partner'].search([('name', '=', 'Azure Interior')])
        

        cls.contract=cls.env['contract.contract'].create({
            'name': cls.name,
            'company_id': cls.company_id.id,
            'partner_id': cls.partner_id.id,
            'contract_line_fixed_ids' : [(0,0,
                                    {
                                    'date_start' : date(2020, 2, 2),
                                    'name' : 'Walrus',
                                    'quantity' : 2.0,
                                    'recurring_interval' : 1,
                                    'recurring_invoicing_type' : 'pre-paid',
                                    'recurring_rule_type' : 'monthly'
                                    }
            )]
        })
        _logger.warning(cls.contract.contract_line_fixed_ids)

            
            
            
            

    @classmethod
    def _create_invoice(cls, description):
        
        invoice=Form(cls.env['contract.contract']) 

    
        invoice.name=cls.name
        invoice.company_id=cls.company_id
        invoice.partner_id=cls.partner_id
        
        with invoice.contract_line_fixed_ids.new() as new_line:
            new_line.date_start = cls.contract.contract_line_fixed_ids.date_start
            new_line.name = description
            new_line.quantity = cls.contract.contract_line_fixed_ids.quantity
            new_line.recurring_interval = cls.contract.contract_line_fixed_ids.recurring_interval
            new_line.recurring_invoicing_type = cls.contract.contract_line_fixed_ids.recurring_invoicing_type
            new_line.recurring_rule_type = cls.contract.contract_line_fixed_ids.recurring_rule_type


        invoice=invoice.save()

        # For some utterly perplexing reason, one finds it necessary to click this button not once, but twice...

        invoice.recurring_create_invoice()
        invoice.recurring_create_invoice()
    
        return invoice 


    
     
    
    def test_prepare_recurring_invoices_values(self):

        _logger.error("HERE1")


        invoice=self._create_invoice("Contract date start: ${object.date_start}")   
        
        invoice = invoice._prepare_recurring_invoices_values()

        assert(invoice[0]['invoice_line_ids'][0][2]['name'] == "Contract date start: 2020-02-02")



    def test_prepare_recurring_invoices_values_with_no_jinja(self):

        _logger.error("HERE2")

        invoice = self._create_invoice("Contract date start: ${object.date_start}")
        
        assert(invoice.contract_line_fixed_ids.name == "Contract date start: ${object.date_start}")


