# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def _create_payment_vals_from_wizard(self, batch_result):
        vals = super()._create_payment_vals_from_wizard(batch_result)
        distribution = batch_result[
            "lines"
        ].move_id._get_reconcile_analytic_distribution()
        if not distribution:
            return vals
        for line_vals in vals["write_off_line_vals"]:
            account = self.env["account.account"].browse(line_vals.get("account_id"))
            if not line_vals.get(
                "analytic_distribution"
            ) and account.internal_group in (
                "income",
                "expense",
            ):
                line_vals["analytic_distribution"] = distribution
        return vals
