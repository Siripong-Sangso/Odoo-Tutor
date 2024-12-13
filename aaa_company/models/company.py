from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    branch_no = fields.Char(string='Branch No.',default='00000')
    company_name_th = fields.Char(string="", help='Company Name (Thai)')
    company_name_eng = fields.Char(string="", help='Company Name (Eng)')