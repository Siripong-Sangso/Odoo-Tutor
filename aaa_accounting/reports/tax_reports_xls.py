from odoo import models, fields, api, _
from lxml import etree
from odoo.tools.safe_eval import safe_eval
from odoo.tools.translate import _
from odoo.exceptions import UserError, Warning
from odoo.tools.misc import formatLang
import time
import datetime
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date


class ReportSaleTaxXLS(models.AbstractModel):
    _name = 'report.aaa_accounting.sale_tax_report_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        report_obj = self.env['report.aaa_accounting.sale_tax_report']

        results = report_obj._get_report_values(obj, data)

        merge_format = workbook.add_format({
            'font_name': 'Angsana New',
            'font_size': 14,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
        })

        merge_format2 = workbook.add_format({
            'font_name': 'Angsana New',
            'bold': True,
            'align': 'left',
            'valign': 'vcenter',
            'font_size': 10,
        })

        merge_format3 = workbook.add_format({
            'font_name': 'Angsana New',
            'align': 'left',
            'valign': 'vcenter',
            'font_size': 10,
        })
        merge_format4 = workbook.add_format({
            'font_name': 'Angsana New',
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 10,
            'bold': True,
            'border': 1,
            'text_wrap': 'true'
        })

        date_format = workbook.add_format(
            {'font_name': 'Angsana New', 'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'border': 1,
             'num_format': 'd/mm/yyyy'})

        currency_format = workbook.add_format(
            {'font_name': 'Angsana New', 'font_size': 10, 'align': 'right', 'valign': 'vcenter', 'border': 1,
             'num_format': '#,##0.00'})

        currency_format2 = workbook.add_format(
            {'font_name': 'Angsana New', 'font_size': 10, 'align': 'right', 'valign': 'vcenter', 'bold': True,
             'border': 1, 'num_format': '#,##0.00'})

        format1 = workbook.add_format(
            {'font_name': 'Angsana New', 'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'bold': True,
             'border': 1})

        format2 = workbook.add_format(
            {'font_name': 'Angsana New', 'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'border': 1})

        format3 = workbook.add_format(
            {'font_name': 'Angsana New', 'font_size': 10, 'align': 'left', 'valign': 'vcenter', 'border': 1})

        sheet = workbook.add_worksheet('รายงานภาษีขาย')

        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 1, 8)
        sheet.set_column(2, 2, 10)
        sheet.set_column(3, 3, 25)
        sheet.set_column(4, 4, 10)
        sheet.set_column(5, 5, 8)
        sheet.set_column(6, 6, 8)
        sheet.set_column(7, 7, 10)
        sheet.set_column(8, 8, 10)

        sheet.merge_range('A1:I1', 'รายงานภาษีขาย', merge_format)

        sheet.merge_range('A2:B2', 'เดือน', merge_format2)
        sheet.merge_range('C2:E2', 'เดือน', merge_format3)
        sheet.merge_range('F2:G2', 'ปี', merge_format2)
        sheet.merge_range('H2:I2', 'เดือน', merge_format3)

        sheet.merge_range('A3:B3', 'ชื่อผู้ประกอบการ', merge_format2)
        sheet.merge_range('C3:E3', 'เดือน', merge_format3)
        sheet.merge_range('F3:G3', 'เลขประจําตัวผู้เสียภาษี', merge_format2)
        sheet.merge_range('H3:I3', 'เดือน', merge_format3)

        sheet.merge_range('A4:B4', 'ชื่อสถานประกอบการ', merge_format2)
        sheet.merge_range('C4:E4', 'เดือน', merge_format3)
        sheet.merge_range('F4:G4', 'สำนักงานใหญ่/สาขา', merge_format2)
        sheet.merge_range('H4:I4', 'เดือน', merge_format3)

        sheet.merge_range('A5:A6', 'ลำดับที่/เล่มที่', merge_format4)
        sheet.merge_range('B5:C5', 'ใบกำกับภาษี', merge_format4)
        sheet.merge_range('D5:D6', 'ชื่อผู้ซื้อสินค้า/ผู้รับบริการ', merge_format4)
        sheet.merge_range('E5:E6', 'เลขประจําตัวผู้เสียภาษีอากรของผู้ซื้อสินค้า', merge_format4)
        sheet.merge_range('F5:G5', 'สถานประกอบการ', merge_format4)
        sheet.merge_range('H5:H6', 'มูลค่าสินค้าหรือบริการ', merge_format4)
        sheet.merge_range('I5:I6', 'จํานวนภาษีมูลค่าเพิ่ม', merge_format4)
        sheet.write('B6', 'วัน เดือน ปี', format1)
        sheet.write('C6', 'เลขที่', format1)
        sheet.write('F6', 'สำนักงานใหญ่', format1)
        sheet.write('G6', 'สาขา', format1)

        row_number = 6
        i = 1
        sum_untaxed = 0
        sum_tax = 0

        for o in results['docs']:
            sum_untaxed = sum_untaxed + (o.balance * 100 / 7)
            sum_tax = sum_tax + o.balance

            sheet.write(row_number, 0, i, format2)
            i += 1
            sheet.write(row_number, 1, o.invoice_date or '', date_format)
            sheet.write(row_number, 2, o.move_id.name or '', format2)
            sheet.write(row_number, 3, o.partner_id.name or '', format3)
            sheet.write(row_number, 4, o.partner_id.vat or '', format3)
            if not int(o.partner_id.branch_no):
                sheet.write(row_number, 5, o.partner_id.branch_no or '', format3)
                sheet.write(row_number, 6, ' ', format3)
            if int(o.partner_id.branch_no):
                sheet.write(row_number, 5, ' ', format3)
                sheet.write(row_number, 6, o.partner_id.branch_no or '', format3)
            if o.debit:
                if o.move_id:
                    sheet.write(row_number, 7, o.move_id.amount_untaxed or '', currency_format)
                if not o.move_id:
                    sheet.write(row_number, 7, o.debit * 100 / 7 or '', currency_format)
                sheet.write(row_number, 8, o.credit or '', currency_format)
            if o.credit:
                if o.move_id:
                    sheet.write(row_number, 7, o.move_id.amount_untaxed or '', currency_format)
                if not o.move_id:
                    sheet.write(row_number, 7, o.credit * 100 / 7 or '', currency_format)
                sheet.write(row_number, 8, o.credit or '', currency_format)
            row_number += 1

        sheet.write(row_number, 6, 'รวม', format1)
        sheet.write(row_number, 7, sum_untaxed * (-1), currency_format2)
        sheet.write(row_number, 8, sum_tax * (-1), currency_format2)

class ReportPurchaseTaxXLS(models.AbstractModel):
    _name = 'report.aaa_accounting.purchase_tax_report_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        report_obj = self.env['report.aaa_accounting.purchase_tax_report']

        results = report_obj._get_report_values(obj, data)

        merge_format = workbook.add_format({
            'font_name': 'Angsana New',
            'font_size': 14,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
        })

        merge_format2 = workbook.add_format({
            'font_name': 'Angsana New',
            'bold': True,
            'align': 'left',
            'valign': 'vcenter',
            'font_size': 10,
        })

        merge_format3 = workbook.add_format({
            'font_name': 'Angsana New',
            'align': 'left',
            'valign': 'vcenter',
            'font_size': 10,
        })
        merge_format4 = workbook.add_format({
            'font_name': 'Angsana New',
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 10,
            'bold': True,
            'border': 1,
            'text_wrap': 'true'
        })

        date_format = workbook.add_format(
            {'font_name': 'Angsana New', 'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'border': 1,
             'num_format': 'd/mm/yyyy'})

        currency_format = workbook.add_format(
            {'font_name': 'Angsana New', 'font_size': 10, 'align': 'right', 'valign': 'vcenter', 'border': 1,
             'num_format': '#,##0.00'})

        currency_format2 = workbook.add_format(
            {'font_name': 'Angsana New', 'font_size': 10, 'align': 'right', 'valign': 'vcenter', 'bold': True,
             'border': 1, 'num_format': '#,##0.00'})

        format1 = workbook.add_format(
            {'font_name': 'Angsana New', 'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'bold': True,
             'border': 1})

        format2 = workbook.add_format(
            {'font_name': 'Angsana New', 'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'border': 1})

        format3 = workbook.add_format(
            {'font_name': 'Angsana New', 'font_size': 10, 'align': 'left', 'valign': 'vcenter', 'border': 1})

        sheet = workbook.add_worksheet('รายงานภาษีซื้อ')

        sheet.set_column(0, 0, 5)
        sheet.set_column(1, 1, 8)
        sheet.set_column(2, 2, 10)
        sheet.set_column(3, 3, 25)
        sheet.set_column(4, 4, 10)
        sheet.set_column(5, 5, 8)
        sheet.set_column(6, 6, 8)
        sheet.set_column(7, 7, 10)
        sheet.set_column(8, 8, 10)

        sheet.merge_range('A1:I1', 'รายงานภาษีซื้อ', merge_format)

        sheet.merge_range('A2:B2', 'เดือน', merge_format2)
        sheet.merge_range('C2:E2', 'เดือน', merge_format3)
        sheet.merge_range('F2:G2', 'ปี', merge_format2)
        sheet.merge_range('H2:I2', 'เดือน', merge_format3)

        sheet.merge_range('A3:B3', 'ชื่อผู้ประกอบการ', merge_format2)
        sheet.merge_range('C3:E3', 'เดือน', merge_format3)
        sheet.merge_range('F3:G3', 'เลขประจําตัวผู้เสียภาษี', merge_format2)
        sheet.merge_range('H3:I3', 'เดือน', merge_format3)

        sheet.merge_range('A4:B4', 'ชื่อสถานประกอบการ', merge_format2)
        sheet.merge_range('C4:E4', 'เดือน', merge_format3)
        sheet.merge_range('F4:G4', 'สำนักงานใหญ่/สาขา', merge_format2)
        sheet.merge_range('H4:I4', 'เดือน', merge_format3)

        sheet.merge_range('A5:A6', 'ลำดับที่/เล่มที่', merge_format4)
        sheet.merge_range('B5:C5', 'ใบกำกับภาษี', merge_format4)
        sheet.merge_range('D5:D6', 'ชื่อผู้ขายสินค้า/ผู้ให้บริการ', merge_format4)
        sheet.merge_range('E5:E6', 'เลขประจําตัวผู้เสียภาษีอากรของขายผู้สินค้า', merge_format4)
        sheet.merge_range('F5:G5', 'สถานประกอบการ', merge_format4)
        sheet.merge_range('H5:H6', 'มูลค่าสินค้าหรือบริการ', merge_format4)
        sheet.merge_range('I5:I6', 'จํานวนภาษีมูลค่าเพิ่ม', merge_format4)
        sheet.write('B6', 'วัน เดือน ปี', format1)
        sheet.write('C6', 'เลขที่', format1)
        sheet.write('F6', 'สำนักงานใหญ่', format1)
        sheet.write('G6', 'สาขา', format1)

        row_number = 6
        i = 1
        sum_untaxed = 0
        sum_tax = 0

        for o in results['docs']:
            sum_untaxed = sum_untaxed + (o.balance * 100 / 7)
            sum_tax = sum_tax + o.balance

            sheet.write(row_number, 0, i, format2)
            i += 1
            sheet.write(row_number, 1, o.invoice_date or '', date_format)
            sheet.write(row_number, 2, o.move_id.name or '', format2)
            sheet.write(row_number, 3, o.partner_id.name or '', format3)
            sheet.write(row_number, 4, o.partner_id.vat or '', format3)
            if not int(o.partner_id.branch_no):
                sheet.write(row_number, 5, o.partner_id.branch_no or '', format3)
                sheet.write(row_number, 6, ' ', format3)
            if int(o.partner_id.branch_no):
                sheet.write(row_number, 5, ' ', format3)
                sheet.write(row_number, 6, o.partner_id.branch_no or '', format3)
            if o.debit:
                if o.move_id:
                    sheet.write(row_number, 7, o.move_id.amount_untaxed or '', currency_format)
                if not o.move_id:
                    sheet.write(row_number, 7, o.debit * 100 / 7 or '', currency_format)
                sheet.write(row_number, 8, o.credit or '', currency_format)
            if o.credit:
                if o.move_id:
                    sheet.write(row_number, 7, o.move_id.amount_untaxed or '', currency_format)
                if not o.move_id:
                    sheet.write(row_number, 7, o.credit * 100 / 7 or '', currency_format)
                sheet.write(row_number, 8, o.credit or '', currency_format)
            row_number += 1

        sheet.write(row_number, 6, 'รวม', format1)
        sheet.write(row_number, 7, sum_untaxed * (-1), currency_format2)
        sheet.write(row_number, 8, sum_tax * (-1), currency_format2)
