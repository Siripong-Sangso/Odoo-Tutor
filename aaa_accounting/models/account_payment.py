# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

class AccountPayment(models.Model):
    _inherit = "account.payment"

    bank_cheque = fields.Boolean(string='Is Cheque', related='journal_id.bank_cheque')
    cheque_reg_id = fields.Many2one('account.cheque.statement', string='Cheque Record')
    cheque_bank = fields.Many2one('res.bank', string="Bank")
    cheque_branch = fields.Char(string="Branch")
    cheque_number = fields.Char(string="Cheque Number")
    cheque_date = fields.Date(string="Cheque Date")