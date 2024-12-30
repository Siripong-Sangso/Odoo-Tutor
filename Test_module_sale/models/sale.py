from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    address_th = fields.Text(string="Address (TH)", search=True)
    address_eng = fields.Text(string="Address (EN)", search=True)
    company_name_th = fields.Char(string="Company Name (TH)")
    company_name_eng = fields.Char(string="Company Name (EN)")

    @api.constrains('company_name_th')
    def _check_company_name_th(self):
        for record in self:
            if record.company_name_th and any(char.isdigit() for char in record.company_name_th):
                raise ValidationError("The Thai company name should not contain any digits.")

    @api.constrains('company_name_eng')
    def _check_company_name_eng(self):
        for record in self:
            if record.company_name_eng and not record.company_name_eng.isalpha():
                raise ValidationError("The English company name should contain only alphabetic characters.")

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





