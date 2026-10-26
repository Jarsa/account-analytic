# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountAnalyticDistributionModel(models.Model):
    _inherit = "account.analytic.distribution.model"

    def _get_applicable_fields(self):
        # Criteria added by account_analytic_auto_assign_* modules, so two
        # models for different operating units or brands do not overlap.
        criteria = set(self._get_default_search_domain_vals()) & set(self._fields)
        return list(dict.fromkeys(super()._get_applicable_fields() + sorted(criteria)))
