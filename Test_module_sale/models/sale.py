from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    partner_mobile = fields.Char(string='Partner Mobile')
    project_number = fields.Char(string='Project Number', required=True)

    _sql_constraints = [
        ('unique_project_number', 'unique(project_number)', 'The Project Number must be unique!'),
    ]

    @api.constrains('partner_mobile')
    def _check_partner_mobile(self):
        for record in self:
            if record.partner_mobile and not record.partner_mobile.isdigit():
                raise ValidationError("The mobile number should contain only digits.")

    @api.constrains('project_number')
    def _check_project_number(self):
        for record in self:
            if record.project_number and len(record.project_number) < 5:
                raise ValidationError("The Project Number must be at least 5 characters long.")