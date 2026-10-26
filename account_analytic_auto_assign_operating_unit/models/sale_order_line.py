# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends("order_id.operating_unit_id")
    def _compute_analytic_distribution(self):  # pylint: disable=missing-return
        for line in self:
            super(
                SaleOrderLine,
                line.with_context(
                    auto_assign_operating_unit_id=line.order_id.operating_unit_id.id
                ),
            )._compute_analytic_distribution()
