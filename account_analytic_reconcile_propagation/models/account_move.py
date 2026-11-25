# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_reconcile_analytic_distribution(self):
        """Distribution of the most recent invoice among ``self``, weighted by
        the amount of each of its lines."""
        invoice = self.filtered(lambda move: move.is_invoice(include_receipts=True))
        invoice = invoice.sorted("date", reverse=True)[:1]
        lines = invoice.invoice_line_ids.filtered("analytic_distribution")
        total = sum(abs(line.balance) for line in lines)
        if not total:
            return {}
        distribution = {}
        for line in lines:
            factor = abs(line.balance) / total
            for key, percentage in line.analytic_distribution.items():
                distribution[key] = distribution.get(key, 0.0) + percentage * factor
        return distribution
