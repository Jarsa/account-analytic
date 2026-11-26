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
        return invoice.invoice_line_ids._get_weighted_analytic_distribution()
