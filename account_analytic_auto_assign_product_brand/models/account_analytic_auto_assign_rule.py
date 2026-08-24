# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountAnalyticAutoAssignRule(models.Model):
    _inherit = "account.analytic.auto.assign.rule"

    product_brand_id = fields.Many2one(
        comodel_name="product.brand",
        ondelete="cascade",
        help="Only applies to lines with products from this brand.",
    )

    def _get_default_search_domain_vals(self):
        return super()._get_default_search_domain_vals() | {
            "product_brand_id": False,
        }
