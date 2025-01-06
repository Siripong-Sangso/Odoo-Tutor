from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    branch_no = fields.Char(string='Branch No.',default='00000')
    company_name_th = fields.Char(string="", help='Company Name (Thai)')
    company_name_eng = fields.Char(string="", help='Company Name (Eng)')
    address_th = fields.Char(string="", help='Address (Thai)')
    address_th_2 = fields.Char(string="", help='Address 2 (Thai)')
    address_eng = fields.Char(string="", help='Address (Eng)')
    address_eng_2 = fields.Char(string="", help='Address 2 (Eng)')
    branch_name = fields.Char(string='Branch Name', default='สำนักงานใหญ่')
    line = fields.Char(string="Line", help='Line')
    ig = fields.Char(string="Instagram", help='Instagram')
    facebook = fields.Char(string="Facebook", help='Facebook')