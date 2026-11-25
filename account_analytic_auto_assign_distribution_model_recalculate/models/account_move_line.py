# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends("move_id.analytic_account_id")
    def _compute_analytic_distribution(self):  # pylint: disable=missing-return
        # account_analytic_distribution_model_recalculate rebuilds the field
        # without calling super(), so the project of the header is applied
        # again on top of its result.
        super()._compute_analytic_distribution()
        self._auto_assign_apply_project()
