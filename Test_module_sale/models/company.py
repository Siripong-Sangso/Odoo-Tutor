from odoo import models, fields, _

class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    address_th = fields.Text(string="Address (TH)")
    address_eng = fields.Text(string="Address (EN)")
