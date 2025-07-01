from odoo import models, fields

class CancelPurchaseMain(models.Model):
    _name = 'cancel.purchase.main'
    _description = 'Cancel Purchase Main Page'

    name = fields.Char(string="Name", default="Cancel Purchase Orders")
    description = fields.Text(string="Description")
