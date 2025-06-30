from collections import defaultdict
from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError


class PurchaseOrderDiscount(models.TransientModel):
    _name = 'purchase.order.discount'
    _description = "Purchase Discount Wizard"

    purchase_order_id = fields.Many2one(
        'purchase.order', default=lambda self: self.env.context.get('active_id'), required=True)
    company_id = fields.Many2one(related='purchase_order_id.company_id')
    currency_id = fields.Many2one(related='purchase_order_id.currency_id')
    discount_amount = fields.Monetary(string="Amount")
    discount_percentage = fields.Float(string="Percentage")
    discount_type = fields.Selection([
        ('pol_discount', "On All Order Lines"),
        ('po_discount', "Global Discount"),
        ('amount', "Fixed Amount"),
    ], default='pol_discount')

    @api.constrains('discount_type', 'discount_percentage')
    def _check_discount_amount(self):
        for wizard in self:
            if wizard.discount_type in ('pol_discount', 'po_discount') and wizard.discount_percentage > 1.0:
                raise ValidationError(_("Invalid discount amount"))

    def _prepare_discount_product_values(self):
        self.ensure_one()
        return {
            'name': _('Purchase Discount'),
            'type': 'service',
            'purchase_ok': True,
            'sale_ok': False,
            'list_price': 0.0,
            'standard_price': 0.0,
            'company_id': self.company_id.id,
            'taxes_id': None,
        }

    def _get_discount_product(self):
        self.ensure_one()
        discount_product = self.company_id.purchase_discount_product_id
        if not discount_product:
            discount_product = self.env['product.product'].create(
                self._prepare_discount_product_values()
            )
            self.company_id.purchase_discount_product_id = discount_product
        return discount_product

    def _prepare_discount_line_values(self, product, amount, taxes, description=None):
        self.ensure_one()
        vals = {
            'order_id': self.purchase_order_id.id,
            'product_id': product.id,
            'price_unit': -amount,
            'product_qty': 1.0,
            'product_uom': product.uom_id.id,
            'taxes_id': [Command.set(taxes.ids)],
            'date_planned': fields.Datetime.now(),
        }
        if description:
            vals['name'] = description
        return vals

    def _create_discount_lines(self):
        self.ensure_one()
        discount_product = self._get_discount_product()
        purchase_order = self.purchase_order_id

        if self.discount_type == 'amount':
            return self.env['purchase.order.line'].create([
                self._prepare_discount_line_values(
                    product=discount_product,
                    amount=self.discount_amount,
                    taxes=self.env['account.tax'],
                )
            ])

        # Handle % global discount
        total_price_per_tax_groups = defaultdict(float)
        for line in purchase_order.order_line:
            if not line.product_qty or not line.price_unit:
                continue
            total_price_per_tax_groups[line.taxes_id] += line.price_subtotal

        if not total_price_per_tax_groups:
            return
        elif len(total_price_per_tax_groups) == 1:
            taxes = next(iter(total_price_per_tax_groups.keys()))
            subtotal = total_price_per_tax_groups[taxes]
            vals_list = [self._prepare_discount_line_values(
                product=discount_product,
                amount=subtotal * self.discount_percentage,
                taxes=taxes,
                description=_("Discount: %(percent)s%%", percent=self.discount_percentage*100),
            )]
        else:
            vals_list = [
                self._prepare_discount_line_values(
                    product=discount_product,
                    amount=subtotal * self.discount_percentage,
                    taxes=taxes,
                    description=_(
                        "Discount: %(percent)s%% - on lines with taxes: %(taxes)s",
                        percent=self.discount_percentage*100,
                        taxes=", ".join(taxes.mapped('name')),
                    )
                ) for taxes, subtotal in total_price_per_tax_groups.items()
            ]

        return self.env['purchase.order.line'].create(vals_list)

    def action_apply_discount(self):
        self.ensure_one()
        self = self.with_company(self.company_id)
        if self.discount_type == 'pol_discount':
            self.purchase_order_id.order_line.write({'discount': self.discount_percentage * 100})
        else:
            self._create_discount_lines()
