# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    @api.depends("product_id.product_brand_id")
    def _compute_analytic_distribution(self):  # pylint: disable=missing-return
        # See account_analytic_auto_assign_operating_unit for why this
        # calls super() first instead of fully rebuilding the field: it
        # lets several sibling modules extending this same compute compose
        # instead of each one overwriting the others' contribution.
        super()._compute_analytic_distribution()
        for expense in self:
            if expense.product_id.product_brand_id:
                extra = self.env[
                    "account.analytic.distribution.model"
                ]._get_distribution(
                    {
                        "product_brand_id": expense.product_id.product_brand_id.id,
                        "company_id": expense.company_id.id,
                    }
                )
                if extra:
                    expense.analytic_distribution = (
                        expense.analytic_distribution or {}
                    ) | extra
