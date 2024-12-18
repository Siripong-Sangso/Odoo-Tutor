from odoo import api, fields, models

class Empty(models.Model):
    _name = "empty"
    _description= "Empty Empty"

    name = fields.Char(string='name', required=True)
    notes = fields.Text(string="Notes")