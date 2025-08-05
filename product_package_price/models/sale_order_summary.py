from odoo import models

class ReportSaleOrderProductSummary(models.AbstractModel):
    _name = 'report.product_package_price.report_sale_order_product_summary'
    _description = 'Grouped Product Summary Report'

    def _get_report_values(self, docids, data=None):
        orders = self.env['sale.order'].browse(docids)
        product_summary = {}

        for order in orders:
            for line in order.order_line:
                product = line.product_id
                if product.id not in product_summary:
                    product_summary[product.id] = {
                        'product': product,
                        'total_boxes': 0.0,
                        'total_pieces': 0.0,
                        'total_qty': 0.0,
                        'uom': line.product_uom.name,
                    }
                product_summary[product.id]['total_boxes'] += line.product_packaging_qty or 0.0
                product_summary[product.id]['total_pieces'] += line.second_product_uom_qty or 0.0
                product_summary[product.id]['total_qty'] += line.product_uom_qty or 0.0

        return {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': list(product_summary.values()),
        }
