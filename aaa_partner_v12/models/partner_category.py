# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
import logging

class PartnerCategory(models.Model):
    _name = 'partner.category'
    _description = 'Partner Category Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "name asc"

    name = fields.Char(string="Name", required=True, track_visibility='onchange')
    code = fields.Char(string="Code", required=True, track_visibility='onchange')
    type = fields.Selection([('retail', 'Retail'), ('whosale', 'Whosale')], string='Type', index=True, default='retail', required=True, track_visibility='onchange')
    notes = fields.Text(string="Note")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id, required=True, track_visibility='onchange')
