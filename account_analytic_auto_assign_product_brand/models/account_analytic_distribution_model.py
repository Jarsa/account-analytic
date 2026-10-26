# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountAnalyticDistributionModel(models.Model):
    _inherit = "account.analytic.distribution.model"

    product_brand_id = fields.Many2one(
        comodel_name="product.brand",
        ondelete="cascade",
        help="Only applies to lines with products of this brand.",
    )

    @api.model
    def _get_default_search_domain_vals(self):
        return super()._get_default_search_domain_vals() | {
            "product_brand_id": False,
        }

    @api.model
    def _get_distribution(self, vals):
        # Every caller (invoice, sale, purchase and expense lines) already
        # passes the product, so the brand is taken from it here.
        if "product_brand_id" not in vals and vals.get("product_id"):
            product = self.env["product.product"].browse(vals["product_id"])
            vals = vals | {"product_brand_id": product.product_brand_id.id}
        return super()._get_distribution(vals)
