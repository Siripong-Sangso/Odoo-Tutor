from odoo import models, fields, api
from datetime import date

class ResPartner(models.Model):

    _inherit = 'res.partner'

    line = fields.Char('Line')
    facebook = fields.Char('Facebook')
    bank_id = fields.Many2one('res.bank', string='Bank')
    account_no = fields.Char('Account No.')
    bank_branch = fields.Char('Bank Branch')
    branch_no = fields.Char(string='Branch No.', default='00000')
    instragram = fields.Char('Instagram')
    birthday = fields.Date(string="Birthday")
    age = fields.Integer(string="Age", compute="_compute_age", store=True)

    @api.depends('birthday')
    def _compute_age(self):
        for partner in self:
            if partner.birthday:
                today = date.today()
                born = fields.Date.from_string(partner.birthday)
                partner.age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            else:
                partner.age = 0
