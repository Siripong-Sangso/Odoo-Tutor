from odoo import models, fields, api

class BarcodeWizard(models.TransientModel):
    _name = 'barcode.wizard'
    _description = 'Barcode Wizard'

    barcode = fields.Char(string='Barcode')
    product_id = fields.Many2one('product.product', string='Product')
    counted_quantity = fields.Float(string='Counted Quantity', default=1.0)
    product_not_found = fields.Boolean(string="Product Not Found", default=False)
    product_show = fields.Many2one('product.product', string='Product', readonly=True)
    lot_id = fields.Many2one('stock.lot', string='Lot/Serial Number',help = 'เก็บค่า Lot หรือ Serial ที่สแกนมา')
    is_serial = fields.Boolean(string = 'Is Serial', compute = '_compute_is_serial',store = True,)

    @ api.depends('product_id')
    def _compute_is_serial(self):
        for rec in self:
                rec.is_serial = bool(rec.product_id and rec.product_id.tracking == 'serial')

    @api.onchange('barcode')
    def _onchange_barcode(self):
        # ตัดช่องว่างหน้า–หลัง แล้วตรวจว่ามีค่าไหม
        code = (self.barcode or '').strip()
        if not code:
            self.product_not_found = False
            return

        product = self.env['product.product'].search([('barcode', '=', code)], limit=1)
        lot = self.env['stock.lot'].search([('name', '=', code)], limit=1)

        if product:
            self.product_id = product.id
            self.product_show = product.id
            self.lot_id = False
            self.product_not_found = False
            if product.tracking == 'serial':
                self.counted_quantity = 1.0


        elif lot:
            # สแกนเจอ serial ใน stock.lot
            self.product_id = lot.product_id.id
            self.product_show = lot.product_id.id
            self.lot_id = lot.id
            self.product_not_found = False
            self.counted_quantity = 1.0

        else:
            self.product_id = False
            self.product_show = False
            self.lot_id = False
            self.product_not_found = True


    def action_add_product(self):
        active_id = self.env.context.get('active_id')
        stock_count = self.env['stock.count'].browse(active_id)

        existing_line = self.env['stock.count.line'].search([
                        ('stock_count_id', '=', stock_count.id),
                        ('product_id', '=', self.product_id.id),
            ], limit=1)

        if self.product_not_found:
            self.env['stock.none'].create({
                'stock_count_id': stock_count.id,
                'barcode': self.barcode,
            })
            self.barcode = False
            return {'type': 'ir.actions.act_window_close'}

        self.env['stock.scan.line'].create({
            'stock_count_id': stock_count.id,
            'product_id': self.product_id.id,
            'counted_quantity': self.counted_quantity,
            'lot_id': self.lot_id.id,
        })

        if existing_line:
            existing_line.counted_quantity += self.counted_quantity
            if self.lot_id:
                existing_line.write({'lot_ids': [(4, self.lot_id.id)]})

        else:
            new_line = self.env['stock.count.line'].create({
                                'stock_count_id': stock_count.id,
                                'product_id': self.product_id.id,
                                'counted_quantity': self.counted_quantity,
                })
            if self.lot_id:
                               new_line.write({'lot_ids': [(4, self.lot_id.id)]})

        return {'type': 'ir.actions.act_window_close'}

    def action_add_stock_none(self):
        stock_count = self.env['stock.count'].browse(self.env.context['active_id'])
        self.env['stock.none.line'].create({
            'stock_count_id': stock_count.id,
            'barcode': self.barcode,
            'counted_quantity': self.counted_quantity,
            'product_id': self.product_id.id or False,
        })
        return {'type': 'ir.actions.act_window_close'}

    # def action_add_and_scan(self):
    #     # ตรวจสอบว่าฟิลด์ barcode มีค่าหรือไม่
    #     if not self.barcode:
    #         raise UserError("Please scan or input a barcode before adding.")
    #
    #     # เรียกใช้ฟังก์ชันเพื่อเพิ่มสินค้า
    #     self.action_add_product()
    #
    #     # ล้างค่าฟิลด์เพื่อตรวจบาร์โค้ดถัดไปโดยไม่ปิด wizard
    #     self.barcode = False
    #     self.product_id = False
    #     self.counted_quantity = 1.0
    #     self.product_not_found = False
    #
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'barcode.wizard',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'context': self.env.context,
    #     }
