from odoo import api, fields, models, _

class EmptyModel(models.Model):
    _name = 'empty.model'
    _inherit = 'mail.thread'
    _description = 'Empty Model'


    name = fields.Char(string="Name")
    age = fields.Integer(string="Age")