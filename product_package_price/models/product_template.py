from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    arabic_name = fields.Char(
        string="Arabic Name",
        compute="_compute_arabic_name",
        inverse="_inverse_arabic_name"
    )

    def _compute_arabic_name(self):
        for rec in self:
            # Switch context to Arabic to read the translated 'name'
            name_ar = rec.with_context(lang='ar_001').name
            rec.arabic_name = name_ar

    def _inverse_arabic_name(self):
        for rec in self:
            # Update the Arabic translation of 'name'
            rec.with_context(lang='ar_001').write({
                'name': rec.arabic_name,
            })
