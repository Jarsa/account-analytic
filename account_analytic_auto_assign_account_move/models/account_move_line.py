# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends("move_id.analytic_account_id")
    def _compute_analytic_distribution(self):  # pylint: disable=missing-return
        super()._compute_analytic_distribution()
        self._auto_assign_apply_project()

    def _auto_assign_apply_project(self):
        for line in self:
            project = line.move_id.analytic_account_id
            if project and line.display_type == "product":
                line.analytic_distribution = project._auto_assign_merge(
                    line.analytic_distribution
                )
