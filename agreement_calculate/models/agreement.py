import logging

from odoo import models, fields, api, _


_logger = logging.getLogger(__name__)


class AgreementReport(models.Model):
    _inherit = "agreement"

    square_meter_per_employee = fields.Float(
            "Square meter/Employee",
            compute="_square_meter_per_employee",
            store=True,
            )

    square_meter_per_workplace = fields.Float(
            "Square meter/Workplace",
            compute="_square_meter_per_workplace",
            store=True,
            )

    yearly_cost_per_square_meter = fields.Float(
            "Yearly cost/Square meter",
            compute="_yearly_cost_per_square_meter",
            store=True,
            )

    yearly_cost_per_employee = fields.Float(
            "Yearly cost/Employee",
            compute="_yearly_cost_per_employee",
            store=True,
            )

    yearly_cost_per_workplace = fields.Float(
            "Yearly cost/Workplace",
            compute="_yearly_cost_per_workplace",
            store=True,
            )

    @api.depends("property_id", "property_id.size", "property_id.size_uom", "yearly_cost")
    def _yearly_cost_per_square_meter(self):
        for record in self:
            calculated_value = None
            try:
                calculated_value = record.yearly_cost / (float(record.property_id.size) * record.property_id.size_uom.factor_inv)
            except (TypeError, ZeroDivisionError) as e:
                pass
            record.yearly_cost_per_square_meter = calculated_value

    @api.depends("property_id", "property_id.employees", "property_id.size", "property_id.size_uom")
    def _square_meter_per_employee(self):
        for record in self:
            calculated_value = None
            try:
                calculated_value = float(record.property_id.size) * record.property_id.size_uom.factor_inv / record.property_id.employees
            except (TypeError, ZeroDivisionError) as e:
                pass
            record.square_meter_per_employee = calculated_value

    @api.depends("property_id", "property_id.employees", "yearly_cost")
    def _yearly_cost_per_employee(self):
        for record in self:
            calculated_value = None
            try:
                calculated_value = record.yearly_cost / record.property_id.employees
            except (TypeError, ZeroDivisionError) as e:
                pass
            record.yearly_cost_per_employee = calculated_value

    @api.depends("property_id", "property_id.size", "property_id.workplaces", "property_id.size_uom")
    def _square_meter_per_workplace(self):
        for record in self:
            calculated_value = None
            try:
                calculated_value = float(record.property_id.size) * record.property_id.size_uom.factor_inv / record.property_id.workplaces
            except (TypeError, ZeroDivisionError) as e:
                pass
            record.square_meter_per_workplace = calculated_value

    @api.depends("property_id", "property_id.workplaces", "yearly_cost")
    def _yearly_cost_per_workplace(self):
        for record in self:
            calculated_value = None
            try:
                calculated_value = record.yearly_cost / record.property_id.workplaces
            except (TypeError, ZeroDivisionError) as e:
                pass
            record.yearly_cost_per_workplace = calculated_value

    def _compute_values(self):
        _logger.warning("calculated_values")
        data = {
#                'SELECT': self._select(),
#                'FROM': self._from(),
#                'WHERE': self._where(),
                }

#        sql_str = "SELECT {SELECT} FROM {FROM} WHERE {WHERE}".format(**data)

#        _logger.warning("SQL command: %s", sql_str)

#        self.env.cr.execute(sql_str)
        from random import randint
        self.my_computed_variable = randint(0,1000)

        _logger.warning("Computed variable: %s", self.my_computed_variable)

        #return super(AgreementReport, self)._compute_values()


