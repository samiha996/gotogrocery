from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_number = fields.Char(string="Customer Number")
