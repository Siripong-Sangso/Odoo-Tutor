# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

class Account_Tax(models.Model):
    _inherit = 'account.tax'

    wht = fields.Boolean(string="WHT")
    tax_report = fields.Boolean(string="Tax Report")
