# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

class AccountJournal(models.Model):
    _inherit = "account.journal"
    _order = 'sequence asc'

    bank_for_cheque_account_id = fields.Many2one('account.account',string='Default Bank Account for Cheque')
    bank_cheque = fields.Boolean(string='Cheque', default=False)



