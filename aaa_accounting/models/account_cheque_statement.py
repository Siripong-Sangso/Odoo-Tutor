# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, date

class AccountChequeStatement(models.Model):
    _name = 'account.cheque.statement'
    _order = "name desc, id desc"


    name = fields.Char(string='ทะเบียนเช็คเลขที่', states={'open': [('readonly', False)]}, copy=False, readonly=True)
    issue_date = fields.Date(required=True, states={'confirm': [('readonly', True)]}, index=True, copy=False, string='วันทีทำรายการ')
    ref = fields.Char(string='อ้างอิง')
    partner_id = fields.Many2one('res.partner',string='Partner')
    cheque_bank = fields.Many2one('res.bank', string="ธนาคาร")
    cheque_branch = fields.Char(string="สาขา")
    cheque_number = fields.Char(string="เช็คเลขที่")
    allow_dup_cheque_no = fields.Boolean(string='รายการซ้ำ')
    cheque_date = fields.Date(string="เช็คลงวันที่")
    amount = fields.Float(string="จำนวนเงิน")
    state = fields.Selection([('open', 'New'), ('confirm', 'Validated'),('cancel', 'Cancel'),('reject', 'Reject')], string='Status', required=True, readonly=True,copy=False, default='open')
    type = fields.Selection([('rec','รับ'),('pay','จ่าย')])
    communication = fields.Char(string='หมายเหตุ')
    validate_date = fields.Date(string='วันที่ตรวจสอบ')
    over_due = fields.Boolean(string='เลยกำหนด',default=False)

    #for technical
    journal_id = fields.Many2one('account.journal',string='ประเภทการจ่ายเงิน')
    move_id = fields.Many2one('account.move', compute="get_move_id",string='รายการบันทึกบัญชีเดิม')
    move_new_id = fields.Many2one('account.move', string='รายการบันทึกบัญชีใหม่')
    payment_id = fields.Many2one('account.payment',string='รายการรับหรือจ่าย')
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company',readonly=True)
    user_id = fields.Many2one('res.users', string='ผู้รับผิดชอบ', required=False, default=lambda self: self.env.user)

    def unlink(self):
        if any(rec.state != 'open' for rec in self):
            raise UserError(_("You can not delete a validated cheque"))
        return super(AccountChequeStatement, self).unlink()


    @api.model
    def check_over_due(self):
        cheque_ids = self.env['account.cheque.statement'].search([('cheque_date', '<', datetime.now().strftime('%m/%d/%Y 00:00:00')),('state','=','open')])
        for cheque in cheque_ids:
            cheque.over_due = True



    @api.onchange('payment_id.move_line_ids')
    def get_move_id(self):
        if self.payment_id.move_line_ids:
            self.move_id = self.payment_id.move_line_ids[0].move_id.id


    @api.model
    def create(self, vals):
        if vals.get('type') == 'rec':
            vals['name'] = self.env['ir.sequence'].next_by_code('cheque.rec.no')
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('cheque.pay.no')
        return super(AccountChequeStatement,self).create(vals)

    def action_validate(self):
        # print "action_validate"
        if not self.validate_date:
            self.validate_date = date.today()

        move_line_vals = self.cheque_move_line_reverse_get()

        line = [(0, 0, l) for l in move_line_vals]

        new_name = ""

        journal_id = self.env['account.journal'].search([('code','=','MISC')],limit=1)

        if journal_id.sequence_id:
            # If invoice is actually refund and journal has a refund_sequence then use that one or use the regular one
            sequence_id = journal_id.sequence_id
            new_name = sequence_id.next_by_id()
            # print "new_new"
            # print new_name
        else:
            raise UserError(_('Please check your journal, system require MISC journal'))

        if move_line_vals:
            move_vals = {
                'ref': self.ref,
                'line_ids': line,
                'journal_id': self.journal_id.id,
                'date': self.validate_date,
                'name': new_name,
                'partner_id' : self.partner_id.id,
                # 'invoice_date': tax_invoice_date,
                'narration': self.communication,
            }
            account_move = self.env['account.move']
            # print "move vals"
            # print move_vals
            move_id = account_move.create(move_vals)
            move_id.post()
            self.write({'move_new_id': move_id.id})
            self.write({'state': 'confirm'})
            self.write({'over_due': False})

    def cheque_move_line_reverse_get(self):
        # print "cheque_move_line_reverse_get"
        res = []
        line_id = self.env['account.move.line'].search([('move_id','=',self.move_id.id),('account_id.is_cheque','=',True)],limit=1)
        original_account_id = line_id.account_id
        new_account_id = self.journal_id.bank_for_cheque_account_id
        debit = credit = 0
        #convert for first statement
        if line_id.debit:
            debit = 0
            credit = line_id.debit
        else:
            debit = line_id.credit
            credit = 0

        # print original_account_id.name
        # print new_account_id.name
        if original_account_id and new_account_id:
            #convert exsting line to remove the exist value
            res.append({
                'date_maturity': self.validate_date,
                'partner_id': self.partner_id.id,
                'ref': self.ref,
                'name': self.name,
                'debit': debit,
                'credit': credit,
                'account_id': original_account_id.id,
                'amount_currency': False,
                'currency_id': False,
                'quantity': 1.00,
                'product_id': False,
                'product_uom_id': False,
                'analytic_account_id': False,
                'invoice_id': False,
                'tax_ids': False,
                'tax_line_id': False,
            })

            #new line for new record
            res.append({
                'date_maturity': self.validate_date,
                'partner_id': self.partner_id.id,
                'ref': self.ref,
                'name': self.name,
                'debit': line_id.debit,
                'credit': line_id.credit,
                'account_id': new_account_id.id,
                'amount_currency': False,
                'currency_id': False,
                'quantity': 1.00,
                'product_id': False,
                'product_uom_id': False,
                'analytic_account_id': False,
                'invoice_id': False,
                'tax_ids': False,
                'tax_line_id': False,
            })

        else:
            raise UserError(_('Please check your journal and accounting setting'))

        # print res
        return res

    def action_cancel(self):
        return self.write({'state':'cancel'})


