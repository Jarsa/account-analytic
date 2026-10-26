# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    def _auto_assign_distribution(self):
        """Distribution this account brings when it is set as the project of
        a document. Extension point, see
        account_analytic_auto_assign_project_distribution."""
        self.ensure_one()
        return {str(self.id): 100.0}

    def _auto_assign_merge(self, distribution):
        """Merge this project into ``distribution`` with the native merge, so
        only the plans touched by the project are replaced and the columns
        filled by the distribution models (branch, brand...) are kept."""
        self.ensure_one()
        new = self._auto_assign_distribution()
        plans = self.browse(
            {int(account) for key in new for account in key.split(",")}
        ).root_plan_id
        return self.env["account.analytic.distribution.model"]._merge_distribution(
            dict(distribution or {}),
            new | {"__update__": [plan._column_name() for plan in plans]},
        )
