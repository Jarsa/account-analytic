# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_analytic_distribution_arguments(self, root_plans):
        arguments = super()._get_analytic_distribution_arguments(root_plans)
        arguments["operating_unit_id"] = self.operating_unit_id.id
        return arguments

    @api.depends("operating_unit_id")
    def _compute_analytic_distribution(self):
        return super()._compute_analytic_distribution()
