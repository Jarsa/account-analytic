# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends("move_id.analytic_account_id")
    def _compute_analytic_distribution(self):  # pylint: disable=missing-return
        super()._compute_analytic_distribution()
        for line in self:
            project = line.move_id.analytic_account_id
            if project and line.display_type == "product":
                line.analytic_distribution = project._auto_assign_merge(
                    line.analytic_distribution
                )

    @api.onchange("product_id")
    def _onchange_product_id_auto_assign_project(self):
        move = self.move_id
        if (
            self.product_id
            and move.move_type in ("in_invoice", "in_refund")
            and not move.analytic_account_id
        ):
            return {
                "warning": {
                    "title": self.env._("Missing project"),
                    "message": self.env._(
                        "Set the project on the bill first, so its lines get"
                        " it automatically."
                    ),
                }
            }
