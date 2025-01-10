# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date, timedelta
from odoo.exceptions import UserError, Warning
from lxml import etree
from odoo.tools.safe_eval import safe_eval
from bahttext import bahttext
from num2words import num2words
import logging

# mapping invoice type to journal type
TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale',
    'in_refund': 'purchase',
}


class CustomerBilling(models.Model):
    _name = 'customer.billing'
    _inherit = ['mail.thread']

    @api.model
    def _default_journal(self):
        inv_type = 'out_invoice'
        inv_types = inv_type if isinstance(inv_type, list) else [inv_type]
        company_id = self._context.get('company_id', self.env.user.company_id.id)
        domain = [
            ('type', 'in', filter(None, map(TYPE2JOURNAL.get, inv_types))),
            ('company_id', '=', company_id),
        ]
        return self.env['account.journal'].search(domain, limit=1)

    @api.model
    def _default_currency(self):
        journal = self._default_journal()
        return journal.currency_id or journal.company_id.currency_id

    @api.depends('invoice_ids')
    def _compute_amount(self):
        self.amount_untaxed = sum(inv.amount_untaxed for inv in self.invoice_ids)
        self.amount_tax = sum(inv.amount_tax for inv in self.invoice_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax

    @api.depends('invoice_ids', 'state')
    def _compute_residual(self):
        self.residual = 0

    name = fields.Char(string='Reference', index=True,
                       readonly=True, states={'draft': [('readonly', False)]}, copy=False, default='New')
    date_billing = fields.Date(string='Billing Date',
                               default=lambda self: self._context.get('date', fields.Date.context_today(self)),
                               copy=False)
    desc = fields.Char('Description', readonly=True, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', string='Customer', change_default=True,
                                 required=True, readonly=True, states={'draft': [('readonly', False)]},
                                 track_visibility='always')
    comment = fields.Text('Additional Information', readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], string='Status', index=True, readonly=True, default='draft', track_visibility='onchange', copy=False,
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Customer billing.\n"
             " * The 'Confirmed' status is used when user create customer billing, a billing number is generated. Its in confirm status till user does not pay the bill amount.\n"
             " * The 'Paid' status is set automatically when the invoices is paid. Its related journal entries may or may not be reconciled.\n"
             " * The 'Cancelled' status is used when user cancel billing.")
    invoice_ids = fields.Many2many('account.move', 'billing_invoice_rel', 'bill_id', 'inv_id',
                                   string='Invoices', readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    invoice_number = fields.Char(string="Invoices", default='', copy=False, compute='_compute_invoice_number')

    user_id = fields.Many2one('res.users', string='Salesperson', track_visibility='onchange',
                              readonly=True, states={'draft': [('readonly', False)]},
                              default=lambda self: self.env.user)
    type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('out_refund', 'Customer Refund'),
    ], readonly=True, index=True, change_default=True, default='out_invoice', track_visibility='always')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True, readonly=True, states={'draft': [('readonly', False)]},
                                  default=_default_currency, track_visibility='always')
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    amount_untaxed = fields.Monetary(string='Untaxed Amount', currency_field='currency_id',
                                     store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    amount_tax = fields.Monetary(string='Tax', currency_field='currency_id',
                                 store=True, readonly=True, compute='_compute_amount')
    amount_total = fields.Monetary(string='Total', currency_field='currency_id',
                                   store=True, readonly=True, compute='_compute_amount')
    residual = fields.Monetary(string='Amount Due', currency_field='currency_id',
                               compute='_compute_residual', store=False, help="Remaining amount due.")

    @api.onchange('partner_id')
    @api.depends('partner_id')
    def onchange_partner_id(self):
        # print self.type
        inv_ids = self.env['account.move'].search(
            [('state', '=', 'posted'), ('move_type', '=', 'out_invoice'),
             ('partner_id', '=', self.partner_id.id), ('billing_id', '=', False),
             ('invoice_date_due', '<=', self.date_billing),
             ('company_id', '=', self.company_id.id)])
        inv_ids = [inv.id for inv in inv_ids]
        self.invoice_ids = [(6, 0, inv_ids)]
        # if self.type == 'out_invoice':
        #     inv_ids = self.env['account.move'].search(
        #         [('state', '=', 'open'), ('move_type', '=', 'out_invoice'),
        #          ('partner_id', '=', self.partner_id.id), ('invoice_date_due', '<=', self.date_billing),
        #          ('company_id', '=', self.company_id.id)])
        #     inv_ids = [inv.id for inv in inv_ids]
        #     self.invoice_ids = [(6, 0, inv_ids)]
        #
        #
        # elif self.type == 'in_invoice':
        #     # print "y"
        #     inv_ids = self.env['account.move'].search(
        #         [('state', '=', 'open'), ('move_type', '=', 'in_invoice'),
        #          ('partner_id', '=', self.partner_id.id), ('invoice_date_due', '<=', self.date_billing),
        #          ('company_id', '=', self.company_id.id)])
        #     inv_ids = [inv.id for inv in inv_ids]
        #     self.invoice_ids = [(6, 0, inv_ids)]

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            if vals.get('type') == 'out_invoice':
                vals['name'] = self.env['ir.sequence'].next_by_code('customer.billing')
            elif vals.get('type') == 'in_invoice':
                vals['name'] = self.env['ir.sequence'].next_by_code('supplier.billing')
        # for inv_id in vals.get('invoice_ids'):
        #     if inv_id[0] == 6:
        #         new_inv_ids = inv_id[2]
        #     if inv_id[0] == 4:
        #         self.env['account.invoice'].browse(inv_id[1]).write({'billing_number': vals['name']})
        # self.env['account.invoice'].browse(inv_id[1]).write({'billing_id': self.id})
        return super(CustomerBilling, self).create(vals)

    def confirm_billing(self, vals):
        for inv_id in self.invoice_ids:
            inv_id.write({'billing_id': self.id})
        self.write({'state': 'confirm'})
        seq = self.env['ir.sequence'].next_by_code('customer.billing.receipt') or 'New'
        self.write({'receipt': seq})

    def action_cancel(self):
        for inv_id in self.invoice_ids:
            inv_id.write({'billing_id': False})
        self.write({'state': 'cancel'})

    def action_cancel_draft(self):
        for inv_id in self.invoice_ids:
            inv_id.write({'billing_id': False})
        self.write({'state': 'draft'})
