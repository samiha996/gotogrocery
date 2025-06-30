from odoo import models, fields

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    package_qty = fields.Float(string="Box Qty")
    pieces_qty = fields.Float(string="Pieces Qty")