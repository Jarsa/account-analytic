# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends("order_id.analytic_account_id")
    def _compute_analytic_distribution(self):  # pylint: disable=missing-return
        # See account_analytic_auto_assign_operating_unit for why this
        # calls super() first instead of fully rebuilding the field: it
        # lets several sibling modules extending this same compute compose
        # instead of each one overwriting the others' contribution. Odoo
        # already carries the result over to the resulting bill line on its
        # own (see purchase/models/account_invoice.py
        # _related_analytic_distribution), so nothing else is needed for it
        # to reach accounting.
        super()._compute_analytic_distribution()
        for line in self:
            if not line.display_type and line.order_id.analytic_account_id:
                line.analytic_distribution = (line.analytic_distribution or {}) | {
                    str(line.order_id.analytic_account_id.id): 100.0
                }
