# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models, _

class ReportSalesDetailedSummary(models.AbstractModel):
    _name = 'report.aaa_sales.report_sales_detailed_summary'

    @api.model
    def _get_report_values(self, docids, data=None):
        # ดึงค่า ids ที่จะใช้ในรายงาน
        sales_ids = data.get('ids', docids)

        # ดึงข้อมูลรายงานที่เชื่อมโยงกับเทมเพลตที่ต้องการใช้
        report = self.env['ir.actions.report']._get_report_from_name('aaa_sales.report_sales_detailed_summary')

        # ส่งค่ากลับสำหรับรายงาน
        return {
            'doc_ids': sales_ids,  # id ของเอกสาร
            'doc_model': 'sale.order',  # โมเดลที่ใช้ในรายงาน
            'docs': self.env['sale.order'].browse(sales_ids),  # ดึงข้อมูลจากโมเดล
            'data': data or {},  # ข้อมูลเพิ่มเติมที่ส่งไปในรายงาน
        }

class ReportSalesSummary(models.AbstractModel):
    _name = 'report.aaa_sales.report_sales_summary'

    @api.model
    def _get_report_values(self, docids, data=None):
        # ดึงค่า ids ที่จะใช้ในรายงาน
        sales_ids = data.get('ids', docids)

        # ดึงข้อมูลรายงานที่เชื่อมโยงกับเทมเพลตที่ต้องการใช้
        report = self.env['ir.actions.report']._get_report_from_name('aaa_sales.report_sales_summary')

        # ส่งค่ากลับสำหรับรายงาน
        return {
            'doc_ids': sales_ids,  # id ของเอกสาร
            'doc_model': 'sale.order',  # โมเดลที่ใช้ในรายงาน
            'docs': self.env['sale.order'].browse(sales_ids),  # ดึงข้อมูลจากโมเดล
            'data': data or {},  # ข้อมูลเพิ่มเติมที่ส่งไปในรายงาน
        }