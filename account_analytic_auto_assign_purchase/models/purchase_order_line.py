# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends("order_id.analytic_account_id")
    def _compute_analytic_distribution(self):  # pylint: disable=missing-return
        super()._compute_analytic_distribution()
        for line in self:
            project = line.order_id.analytic_account_id
            if project and not line.display_type:
                line.analytic_distribution = project._auto_assign_merge(
                    line.analytic_distribution
                )
