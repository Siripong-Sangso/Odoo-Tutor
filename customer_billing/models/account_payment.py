# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2021. All rights reserved.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'out_receipt': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
    'in_receipt': 'supplier',
}

MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': 1,
    'in_invoice': -1,
    'out_refund': -1,
}


class RegisterBillingPayments(models.Model):
    _inherit = "account.payment"

    has_invoices = fields.Boolean(help="Technical field used for usability purposes")

    @api.depends('invoice_ids')
    def _get_has_invoices(self):
        self.has_invoices = bool(self.invoice_ids)

    def _get_invoices(self):
        context = dict(self._context or {})
        active_id = context.get('active_id')
        billing = self.env[context.get('active_model')].browse(active_id)
        invoice_ids = [invoice.id for invoice in billing.invoice_ids]
        invoices = self.env['account.move'].search([('state', '=', 'posted'), ('id', 'in', invoice_ids)])
        return invoices

    def _compute_payment_amount(self, invoices, currency, journal, date):
        '''Compute the total amount for the payment wizard.

        :param invoices:    Invoices on which compute the total as an account.invoice recordset.
        :param currency:    The payment's currency as a res.currency record.
        :param journal:     The payment's journal as an account.journal record.
        :param date:        The payment's date as a datetime.date object.
        :return:            The total amount to pay the invoices.
        '''
        company = journal.company_id
        currency = currency or journal.currency_id or company.currency_id
        date = date or fields.Date.today()

        if not invoices:
            return 0.0

        self.env['account.move'].flush(['move_type', 'currency_id'])
        self.env['account.move.line'].flush(['amount_residual', 'amount_residual_currency', 'move_id', 'account_id'])
        self.env['account.account'].flush(['user_type_id'])
        self.env['account.account.type'].flush(['type'])
        self._cr.execute('''
            SELECT
                move.move_type AS type,
                move.currency_id AS currency_id,
                SUM(line.amount_residual) AS amount_residual,
                SUM(line.amount_residual_currency) AS residual_currency
            FROM aaa_stock move
            LEFT JOIN account_move_line line ON line.move_id = move.id
            LEFT JOIN account_account account ON account.id = line.account_id
            LEFT JOIN account_account_type account_type ON account_type.id = account.user_type_id
            WHERE move.id IN %s
            AND account_type.type IN ('receivable', 'payable')
            GROUP BY move.id, move.move_type
        ''', [tuple(invoices.ids)])
        query_res = self._cr.dictfetchall()

        total = 0.0
        for res in query_res:
            move_currency = self.env['res.currency'].browse(res['currency_id'])
            if move_currency == currency and move_currency != company.currency_id:
                total += res['residual_currency']
            else:
                total += company.currency_id._convert(res['amount_residual'], currency, company, date)
        return total


    @api.model
    def default_get(self, default_fields):
        rec = super(RegisterBillingPayments, self).default_get(default_fields)

        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')
        if not active_ids or active_model != 'customer.billing':
            return rec

        if not active_model or not active_ids:
            raise UserError(
                _("Programmation error: wizard action executed without active_model or active_ids in context."))
        if active_model != 'customer.billing':
            raise UserError(_(
                "Programmation error: the expected model for this action is 'customer.billing'. The provided one is '%d'.") % active_model)

        invoices = self._get_invoices()
        if not invoices or any(invoice.state != 'posted' for invoice in invoices):
            raise UserError(_("You can only register payments for open invoices"))
        dtype = invoices[0].move_type
        for inv in invoices[1:]:
            if inv.move_type != dtype:
                if ((dtype == 'in_refund' and inv.type == 'in_invoice') or
                        (dtype == 'in_invoice' and inv.type == 'in_refund')):
                    raise UserError(
                        _("You cannot register payments for vendor bills and supplier refunds at the same time."))
                if ((dtype == 'out_refund' and inv.type == 'out_invoice') or
                        (dtype == 'out_invoice' and inv.type == 'out_refund')):
                    raise UserError(
                        _("You cannot register payments for customer invoices and credit notes at the same time."))

        amount = self._compute_payment_amount(invoices, invoices[0].currency_id, invoices[0].journal_id,
                                              rec.get('payment_date') or fields.Date.today())
        rec.update({
            'currency_id': invoices[0].currency_id.id,
            'amount': abs(amount),
            'payment_type': 'inbound' if amount > 0 else 'outbound',
            'partner_id': invoices[0].commercial_partner_id.id,
            'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].move_type],
            'communication': invoices[0].ref or invoices[0].name,
            'invoice_ids': [(6, 0, invoices.ids)],
        })
        return rec



    def get_payment_vals(self):
        res = {
            'journal_id': self.journal_id.id,
            'payment_method_id': self.payment_method_id.id,
            'payment_date': self.payment_date,
            'communication': self.communication,
            'invoice_ids': [(4, inv.id, None) for inv in self._get_invoices()],
            'payment_type': self.payment_type,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_type': self.partner_type,
        }
        return res

    def create_payment(self):
        context = dict(self._context or {})
        active_id = context.get('active_id')
        payment = self.env['account.payment'].create(self.get_payment_vals())
        payment.post()
        bill_record = self.env[context.get('active_model')].browse(active_id)
        if bill_record.residual <= 0:
            bill_record.write({'state': 'paid'})
        return {'type': 'ir.actions.act_window_close'}
