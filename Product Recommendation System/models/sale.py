from odoo import models, fields, api
from collections import Counter


class ProductRecommendation(models.Model):
    _inherit = 'sale.order'

    recommended_products = fields.Many2many('product.product', string="Recommended Products")

    def action_recommend_products(self):
        # ดึงข้อมูลการขายทั้งหมด
        orders = self.env['sale.order.line'].search([])
        product_counts = Counter()

        # นับจำนวนสินค้าที่ขาย
        for line in orders:
            product_counts[line.product_id.id] += line.product_uom_qty

        # สินค้าที่ขายดี (Top 5)
        top_products = product_counts.most_common(5)
        product_ids = [product[0] for product in top_products]

        # เพิ่มสินค้าแนะนำในฟิลด์
        self.recommended_products = [(6, 0, product_ids)]

    def action_cross_sell_products(self):
        # สินค้าที่เคยขายร่วมกัน
        cross_sell_products = Counter()

        # ดึงข้อมูลสินค้าที่ลูกค้าซื้อพร้อมกัน
        for order in self.env['sale.order'].search([]):
            products_in_order = [line.product_id.id for line in order.order_line]
            for product in products_in_order:
                for other_product in products_in_order:
                    if product != other_product:
                        cross_sell_products[(product, other_product)] += 1

        # แสดงผลสินค้าที่เกี่ยวข้อง
        cross_sell_suggestions = [pair[1] for pair in cross_sell_products.most_common(5)]
        self.recommended_products = [(6, 0, cross_sell_suggestions)]
