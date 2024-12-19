from odoo import models, fields

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    partner_mobile = fields.Integer(string='Partner Mobile')