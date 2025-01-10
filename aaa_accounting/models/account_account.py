# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

class Account(models.Model):
    _inherit = "account.account"

    is_cheque = fields.Boolean(string='Account for Cheque',default=False)