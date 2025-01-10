# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
from lxml import etree
from odoo.tools.safe_eval import safe_eval
import logging
from bahttext import bahttext
from num2words import num2words


class BookWithholdingTax(models.Model):
    _name = 'book.withholding.tax'
    _description = 'Book Withholding Tax Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "name asc"

    name = fields.Char(string="เล่มที่", default="เล่มที่", required=True, track_visibility='always')
    count_no = fields.Integer(string='ลำดับที่*', copy=False)
    notes = fields.Text(string="Note", track_visibility='always')
    is_use = fields.Boolean(string='ใช้งาน')

class TypeWithholding(models.Model):
    _name = 'type.withholding'
    _description = 'Type Withholding Tax Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "name asc"

    name = fields.Char(string="ประเภทเงินได้", default="ประเภทเงินได้", required=True, track_visibility='always')
    notes = fields.Text(string="Note", track_visibility='always')


class WithholdingTax(models.Model):
    _name = 'withholding.tax'
    _description = 'Withholding Tax'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.depends('wht_line.untaxed_amount', 'wht_line.vat', 'wht_line.total_amount', 'wht_line.wht_tax', 'wht_line.paid_amount')
    def _compute_amount(self):
        self.untaxed_amount = sum(line.untaxed_amount for line in self.wht_line)
        self.vat = sum(line.vat for line in self.wht_line)
        self.total_amount = sum(line.total_amount for line in self.wht_line)
        self.wht_tax = sum(line.wht_tax for line in self.wht_line)
        self.paid_amount = sum(line.paid_amount for line in self.wht_line)
        self.amount_total = self.wht_tax
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'เสร็จสิ้น'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, default='draft', track_visibility='always')


    name = fields.Char(string="เลขที่", default='Draft Contract', readonly=True, required=True, track_visibility='always')
    reference = fields.Char(string="Reference")
    book_ids = fields.Many2one('book.withholding.tax', readonly=True, string='เล่มที่', default=lambda self: self.env['book.withholding.tax'].search([('id', '=', 1)]))
    book_count_no = fields.Integer(string="ลำดับที่*", related='book_ids.count_no', help="ลำดับที่*")
    order_date = fields.Date(string='วันที่', default=lambda self: fields.date.today(), help="วันที่",
                             track_visibility='always')
    vendor_id = fields.Many2one('res.partner', string="ชื่อผู้จำหน่าย", track_visibility='always')
    wht_form = fields.Selection([('wht_3', 'ภงด 3'),
                                 ('wht_53', 'ภงด 53'),
                                 ('wht_1_a', 'ภงด 1ก'),
                                 ('wht_1_s', 'ภงด 1ก(พิเศษ)'),
                                 ('wht_2', 'ภงด 2'),
                                 ('wht_2_a', 'ภงด 2ก'),
                                 ('wht_3_a', 'ภงด 3ก')],
                                string='แบบฟอร์ม', required=True, track_visibility='always', store=True)
    paid_in = fields.Selection([
        ('paid_1', 'ภาษีหัก ณ ที่จ่าย'),
        ('paid_2', 'ออกภาษีให้ตลอดไป'),
        ('paid_3', 'ออกภาษีให้ครั้งเดียว'),
        ('paid_4', 'อื่นๆ')
    ], 'ผู้จ่ายเงิน', required=True, track_visibility='always', store=True)
    paid_etc = fields.Char(string=" ")
    detail = fields.Text(string='หมายเหตุ', track_visibility='always')
    notes = fields.Text(string="โน๊ตภายในบริษัทฯ", track_visibility='always')

    untaxed_amount = fields.Float(string='จำนวนเงิน (ไม่รวมภาษี)', readonly=True, compute='_compute_amount')
    vat = fields.Float(string='ภาษีมูลค่าเพิ่ม 7%', readonly=True, compute='_compute_amount')
    total_amount = fields.Float(string='จำนวนเงิน', readonly=True, compute='_compute_amount')
    wht_tax = fields.Float(string='ภาษีที่หัก', readonly=True, compute='_compute_amount')
    amount_total = fields.Float(string='ภาษีที่หัก', readonly=True, compute='_compute_amount')
    paid_amount = fields.Float(string='ยอดชำระ', readonly=True, compute='_compute_amount')

    wht_line = fields.One2many('withholding.tax.line', 'wht_id', string='Line Withholding Tax', copy=True)
    company_id = fields.Many2one('res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get('withholding.tax'))


    def action_open(self):
        for rec in self:
            rec.state = "done"
            if rec.name == "Draft Contract":
                sequence_code = 'withholding.tax'
                order_date = rec.order_date
                rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=order_date).next_by_code(sequence_code)


    def action_cancel(self):
        for rec in self:
            rec.state = "cancel"


    def baht_text(self, amount_total):
        return bahttext(amount_total)

    def num2_words(self, amount_total):
        before_point = ""
        amount_total_str = str(amount_total)
        for i in range(0,len(amount_total_str)):
            if amount_total_str[i] != ".":
                before_point += amount_total_str[i]
            else:
                break

        after_point = float(amount_total) - float(before_point)
        after_point = locale.format("%.2f", float(after_point), grouping=True)
        after_point = float(after_point)
        before_point = float(before_point)

        # print before_point
        # print after_point
        before_point_str = num2words(before_point)
        after_point_str = num2words(after_point)
        if after_point_str == 'zero':
            before_point_str += ' Only'
        else:
            for i in range(4,len(after_point_str)):
                before_point_str += after_point_str[i]

        n2w_origianl = before_point_str
        #print n2w_origianl
        # n2w_origianl = num2words(float(amount_total))
        n2w_new = ""
        for i in range(len(n2w_origianl)):
            if i == 0:
                n2w_new += n2w_origianl[i].upper()
            else:
                if n2w_origianl[i] != ",":
                    if n2w_origianl[i - 1] == " ":
                        n2w_new += n2w_origianl[i].upper()
                    else:
                        n2w_new += n2w_origianl[i]

        # print n2w_origianl
        # print n2w_new
        return n2w_new






class LineWithholdingTax(models.Model):
    _name = 'withholding.tax.line'
    _description = 'Line Withholding Tax'

    def _compute_amount(self):
        if self.type_wht_tax == 'wht_tax_3%':
            wht_tax = 3
            net_wht_tax = (wht_tax / 100)
        elif self.type_wht_tax == 'wht_tax_5%':
            wht_tax = 5
            net_wht_tax = (wht_tax / 100)
        elif self.type_wht_tax == 'wht_tax_0_5%':
            wht_tax = 0.5
            net_wht_tax = (wht_tax / 100)
        elif self.type_wht_tax == 'wht_tax_0_75%':
            wht_tax = 0.75
            net_wht_tax = (wht_tax / 100)
        elif self.type_wht_tax == 'wht_tax_1%':
            wht_tax = 1
            net_wht_tax = (wht_tax / 100)
        elif self.type_wht_tax == 'wht_tax_1_5%':
            wht_tax = 1.5
            net_wht_tax = (wht_tax / 100)
        elif self.type_wht_tax == 'wht_tax_2%':
            wht_tax = 2
            net_wht_tax = (wht_tax / 100)
        elif self.type_wht_tax == 'wht_tax_10%':
            wht_tax = 10
            net_wht_tax = (wht_tax / 100)
        elif self.type_wht_tax == 'wht_tax_15%':
            wht_tax = 15
            net_wht_tax = (wht_tax / 100)
        elif self.type_wht_tax == 'wht_tax_amount':
            wht_tax = self.input_wht_tax
            net_wht_tax = wht_tax

        if self.type_income == 'type4_b_1_4':
            wht_tax = self.type_wht_tax_1_4
            net_wht_tax = (wht_tax / 100)

        if self.type_wht_tax != 'wht_tax_amount':
            if self.wht_vat == 'non_vat':
                self.untaxed_amount = self.amount
                self.vat = self.amount * (7 / 100)
                self.total_amount = self.amount + self.vat
                self.wht_tax = self.untaxed_amount * net_wht_tax
                self.paid_amount = self.total_amount - self.wht_tax

            elif self.wht_vat == 'vat':
                self.untaxed_amount = (self.amount * 100) / 107
                self.vat = self.amount - self.untaxed_amount
                self.total_amount = self.amount + self.vat
                self.wht_tax = self.untaxed_amount * net_wht_tax
                self.paid_amount = self.total_amount - self.wht_tax

            elif self.wht_vat == 'except_vat':
                self.untaxed_amount = self.amount
                self.vat = 0
                self.total_amount = self.amount
                self.wht_tax = self.untaxed_amount * net_wht_tax
                self.paid_amount = self.total_amount - self.wht_tax
        else:
            if self.wht_vat == 'non_vat':
                self.untaxed_amount = self.amount
                self.vat = self.amount * (7 / 100)
                self.total_amount = self.amount + self.vat
                self.wht_tax = net_wht_tax
                self.paid_amount = self.total_amount - self.wht_tax

            elif self.wht_vat == 'vat':
                self.untaxed_amount = (self.amount * 100) / 107
                self.vat = self.amount - self.untaxed_amount
                self.total_amount = self.amount + self.vat
                self.wht_tax = net_wht_tax
                self.paid_amount = self.total_amount - self.wht_tax

            elif self.wht_vat == 'except_vat':
                self.untaxed_amount = self.amount
                self.vat = 0
                self.total_amount = self.amount
                self.wht_tax = net_wht_tax
                self.paid_amount = self.total_amount - self.wht_tax


    wht_id = fields.Many2one('withholding.tax', string='Withholding Tax', index=True, required=True,
                             ondelete='cascade')
    type = fields.Many2one('type.withholding', string='ประเภท')
    type_income = fields.Selection([('type1', '1. เงินเดือน ค่าจ้าง เบี้ยเลี้ยง โบนัส ฯลฯ ตามมาตรา 40 (1)'),
                                    ('type2', '2. ค่าธรรมเนียม ค่านายหน้า ฯลฯ ตามมาตรา 40 (2)'),
                                    ('type3', '3. ค่าแห่งลิขสิทธิ์ ฯลฯ ตามมาตรา 40(3)'),
                                    ('type4_a', '4. (ก) ค่าดอกเบี้ย ฯลฯ ตามมาตรา 40(4) (ก)'),
                                    ('type4_b_1_1',
                                     '4. (ข)(1.1) กิจการที่ต้องเสียภาษีเงินได้นิติบุคคลในอัตราร้อยละ 30 ของกำไรสุทธิ'),
                                    ('type4_b_1_2',
                                     '4. (ข)(1.2) กิจการที่ต้องเสียภาษีเงินได้นิติบุคคลในอัตราร้อยละ 25 ของกำไรสุทธิ'),
                                    ('type4_b_1_3',
                                     '4. (ข)(1.3) กิจการที่ต้องเสียภาษีเงินได้นิติบุคคลในอัตราร้อยละ 20 ของกำไรสุทธิ'),
                                    ('type4_b_1_4',
                                     '4. (ข)(1.4) กิจการที่ต้องเสียภาษีเงินได้นิติบุคคลในอัตราอื่นๆ ของกำไรสุทธิ (กรุณาระบุ)'),
                                    ('type4_b_2_1', '4. (ข)(2.1) กำไรสุทธิของกิจการที่ได้รับยกเว้นเงินได้นิติบุคคล'),
                                    ('type4_b_2_2', '4. (ข)(2.2) เงินปันผลหรือเงินส่วนแบ่งของกำไรที่ได้รับยกเว้น...'),
                                    ('type4_b_2_3',
                                     '4. (ข)(2.3) กำไรสุทธิส่วนที่ได้หักผลขาดทุนสิทธิยกมาไม่เกิน 5 ปี...'),
                                    ('type4_b_2_4',
                                     '4. (ข)(2.4) กำไรที่รับรู้ทางบัญชีโดยวิธีส่วนได้เสีย (equity method)'),
                                    ('type4_b_2_5', '4. (ข)(2.5) อื่นๆ (กรุณาระบุ)'),
                                    ('type5', '5. การจ่ายเงินได้ที่ต้องหักภาษี ณ ที่จ่ายตามคำสั่งกรมสรรพากร....'),
                                    ('type6', '6. อื่นๆ (กรุณาระบุ)')],
                                   string='ประเภทเงินได้ที่จ่าย', required=True, track_visibility='always', store=True)
    type_wht_tax = fields.Selection([('wht_tax_3%', '3%'),
                                     ('wht_tax_5%', '5%'),
                                     ('wht_tax_0_5%', '0.5%'),
                                     ('wht_tax_0_75%', '0.75%'),
                                     ('wht_tax_1%', '1%'),
                                     ('wht_tax_1_5%', '1.5%'),
                                     ('wht_tax_2%', '2%'),
                                     ('wht_tax_10%', '10%'),
                                     ('wht_tax_15%', '15%'),
                                     ('wht_tax_amount', 'จำนวนเงิน')],
                                    string='อัตราภาษีที่หัก', required=True, track_visibility='always', store=True)
    input_wht_tax = fields.Float(string='ภาษีที่หัก')
    wht_vat = fields.Selection([('non_vat', 'ไม่รวมภาษีมูลค่าเพิ่ม'),
                                ('vat', 'รวมภาษีมูลค่าเพิ่ม'),
                                ('except_vat', 'ไม่มี/ยกเว้นภาษีมูลค่าเพิ่ม')],
                               string='ภาษีมูลค่าเพิ่ม', required=True, track_visibility='always', store=True)

    amount = fields.Float(string='จำนวนเงิน')
    untaxed_amount = fields.Float(string='จำนวนเงิน(ไม่รวมภาษี)', compute='_compute_amount')
    vat = fields.Float(string='ภาษี', compute='_compute_amount')
    total_amount = fields.Float(string='จำนวนเงิน', compute='_compute_amount')
    wht_tax = fields.Float(string='ภาษีที่หักและนำส่งไว้', compute='_compute_amount')
    paid_amount = fields.Float(string='จำนวนเงินที่จ่าย', compute='_compute_amount')
    type6_note = fields.Char(string="")
    type_wht_tax_1_4 = fields.Float(string='อัตราอื่นๆ')
