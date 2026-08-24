# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("product_id.product_brand_id")
    def _compute_analytic_distribution(self):  # pylint: disable=missing-return
        # See account_analytic_auto_assign_operating_unit for why this
        # calls super() first instead of fully rebuilding the field: it
        # lets several sibling modules extending this same compute compose
        # instead of each one overwriting the others' contribution.
        super()._compute_analytic_distribution()
        for line in self:
            if not line.display_type and line.product_id.product_brand_id:
                extra = line.env[
                    "account.analytic.distribution.model"
                ]._get_distribution(
                    {
                        "product_brand_id": line.product_id.product_brand_id.id,
                        "company_id": line.company_id.id,
                    }
                )
                if extra:
                    line.analytic_distribution = (
                        line.analytic_distribution or {}
                    ) | extra
