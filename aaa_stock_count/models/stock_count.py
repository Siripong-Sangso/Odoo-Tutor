from odoo import models, fields, api

class StockCount(models.Model):
    _name = 'stock.count'
    _description = 'Stock Count'

    name = fields.Char(string='Stock Count Reference', required=True, copy=False, readonly=True, default=lambda self: 'New')
    date = fields.Datetime(string='Count Date', required=True, default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', string='Responsible User', default=lambda self: self.env.user, readonly=True)
    count_type = fields.Selection([
        ('all', 'Count All'),
        ('warehouse', 'Count by Warehouse'),
        ('location', 'Count by Location')
    ], string='Count Type', required=True, default='all')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    location_id = fields.Many2one('stock.location', string='Location')
    line_ids = fields.One2many('stock.count.line', 'stock_count_id', string='Stock Count Lines')
    scan_line_ids = fields.One2many('stock.scan.line', 'stock_count_id', string='Scan Lines')
    none_line_ids = fields.One2many('stock.none.line','stock_count_id',string='Not Found Scans',)
    lot_ids = fields.Many2one('stock.lot', string='Lot/Serial Number', help='เก็บค่า Lot หรือ Serial ที่สแกนมา')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    discrepancy_found = fields.Boolean(string='Discrepancy Found', compute='_compute_discrepancy')

    @api.depends('line_ids.new_quantity')
    def _compute_discrepancy(self):
        for record in self:
            record.discrepancy_found = any(line.counted_quantity != line.system_quantity for line in record.line_ids)

    def action_validate(self):
        if self.state == 'draft':
            # Generate the name only when validating
            if self.name == 'New':
                self.name = self.env['ir.sequence'].next_by_code('stock.count') or 'New'

            for line in self.line_ids:
                line.new_quantity = line.counted_quantity  # Update the new quantity based on counted quantity

            self.state = 'done'
        return self.action_compare()

    def action_compare(self):
        for line in self.line_ids:
            if line.counted_quantity != line.system_quantity:
                line.discrepancy = True
            else:
                line.discrepancy = False
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.count',
            'view_mode': 'form',
            'res_id': self.id,
        }

    @api.onchange('count_type')
    def _onchange_count_type(self):
        if self.count_type != 'warehouse':
            self.warehouse_id = False
        if self.count_type != 'location':
            self.location_id = False
        if self.line_ids:
            self._update_system_quantities()

    def _update_system_quantities(self):
        for line in self.line_ids:
            line._compute_system_quantity()


class StockCountLine(models.Model):
    _name = 'stock.count.line'
    _description = 'Stock Count Line'

    stock_count_id = fields.Many2one('stock.count', string='Stock Count Reference', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product')
    counted_quantity = fields.Float(string='Counted Quantity', required=True)
    system_quantity = fields.Float(string='System Quantity', compute='_compute_system_quantity', store=True)
    new_quantity = fields.Float(string='New Quantity', compute='_compute_new_quantity')
    discrepancy = fields.Boolean(string='Discrepancy', default=False)
    lot_ids = fields.Many2many('stock.lot', 'stock_count_line_lot_rel', 'line_id', 'lot_id', string = 'Lot/Serial Numbers', help = 'เก็บทุก Lot/Serial ที่สแกนมา')

    @api.depends('counted_quantity')
    def _compute_new_quantity(self):
        for line in self:
            line.new_quantity = line.counted_quantity

    @api.depends('product_id', 'stock_count_id.count_type', 'stock_count_id.warehouse_id', 'stock_count_id.location_id')
    def _compute_system_quantity(self):
        for line in self:
            if line.stock_count_id.count_type == 'all':
                line.system_quantity = line.product_id.qty_available
            elif line.stock_count_id.count_type == 'warehouse':
                warehouse_quant = self.env['stock.quant'].search([
                    ('product_id', '=', line.product_id.id),
                    ('location_id', 'child_of', line.stock_count_id.warehouse_id.lot_stock_id.id)
                ])
                line.system_quantity = sum(warehouse_quant.mapped('quantity'))
            elif line.stock_count_id.count_type == 'location':
                location_quant = self.env['stock.quant'].search([
                    ('product_id', '=', line.product_id.id),
                    ('location_id', '=', line.stock_count_id.location_id.id)
                ])
                line.system_quantity = sum(location_quant.mapped('quantity'))


class StockScanLine(models.Model):
    _name = 'stock.scan.line'
    _description = 'Stock Scan Line'

    stock_count_id = fields.Many2one('stock.count', string='Stock Count', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    counted_quantity = fields.Float(string='Counted Quantity', required=True)
    system_quantity = fields.Float(string='System Quantity', compute='_compute_system_quantity', store=True)
    new_quantity = fields.Float(string='New Quantity', compute='_compute_new_quantity')
    discrepancy = fields.Boolean(string='Discrepancy', default=False)
    lot_id = fields.Many2one('stock.lot', string='Lot/Serial Number',help = 'เก็บค่า Lot หรือ Serial ที่สแกนมา')
    is_serial = fields.Boolean(string = 'Is Serial',compute = '_compute_is_serial',store = True,)


    @ api.depends('product_id')
    def _compute_is_serial(self):
        for rec in self:
                rec.is_serial = bool(rec.product_id and rec.product_id.tracking == 'serial')

    @api.depends('counted_quantity')
    def _compute_new_quantity(self):
        for line in self:
            line.new_quantity = line.counted_quantity

    @api.depends('product_id', 'stock_count_id.count_type', 'stock_count_id.warehouse_id', 'stock_count_id.location_id')
    def _compute_system_quantity(self):
        for line in self:
            ctype = line.stock_count_id.count_type
            if ctype == 'all':
                # นับทั้งหมด
                line.system_quantity = line.product_id.qty_available
            elif ctype == 'warehouse' and line.stock_count_id.warehouse_id:
                # นับตาม warehouse
                quants = self.env['stock.quant'].search([
                    ('product_id', '=', line.product_id.id),
                    ('location_id', 'child_of', line.stock_count_id.warehouse_id.lot_stock_id.id),
                ])
                line.system_quantity = sum(quants.mapped('quantity'))
            elif ctype == 'location' and line.stock_count_id.location_id:
                # นับตาม location
                quants = self.env['stock.quant'].search([
                    ('product_id', '=', line.product_id.id),
                    ('location_id', '=', line.stock_count_id.location_id.id),
                ])
                line.system_quantity = sum(quants.mapped('quantity'))
            else:
                # กรณีไม่มี warehouse/location หรือเงื่อนไขอื่น ๆ
                line.system_quantity = 0.0


class StockNoneLine(models.Model):
    _name = 'stock.none.line'
    _description = 'Stock None Line'

    stock_count_id    = fields.Many2one('stock.count', string='Stock Count', required=True)
    product_id        = fields.Many2one('product.product', string='Product')
    counted_quantity  = fields.Float(string='Counted Quantity', required=True)
    barcode           = fields.Char(string='Scanned Barcode')