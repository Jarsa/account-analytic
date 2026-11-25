# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountAnalyticAccount(models.Model):
    _name = "account.analytic.account"
    _inherit = ["account.analytic.account", "analytic.mixin"]

    def _auto_assign_distribution(self):
        """The project itself goes in every key of its predefined split."""
        self.ensure_one()
        if not self.analytic_distribution:
            return super()._auto_assign_distribution()
        project = str(self.id)
        return {
            key if project in key.split(",") else f"{project},{key}": percentage
            for key, percentage in self.analytic_distribution.items()
        }
