# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # branch_no = fields.Char(string='Branch No.',default='00000')