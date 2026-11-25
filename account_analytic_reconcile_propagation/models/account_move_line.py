# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def _prepare_reconciliation_single_partial(
        self, debit_values, credit_values, shadowed_aml_values=None
    ):
        # The exchange difference is prepared on one side only (often the
        # payment), so both sides are passed on to find the invoice.
        amls = debit_values["aml"] | credit_values["aml"]
        return super(
            AccountMoveLine, self.with_context(reconcile_analytic_aml_ids=amls.ids)
        )._prepare_reconciliation_single_partial(
            debit_values, credit_values, shadowed_aml_values=shadowed_aml_values
        )

    def _prepare_exchange_difference_move_vals(
        self, amounts_list, company=None, exchange_date=None, **kwargs
    ):
        if not kwargs.get("exchange_analytic_distribution"):
            amls = self | self.browse(
                self.env.context.get("reconcile_analytic_aml_ids", [])
            )
            distribution = amls.move_id._get_reconcile_analytic_distribution()
            if distribution:
                kwargs["exchange_analytic_distribution"] = distribution
        return super()._prepare_exchange_difference_move_vals(
            amounts_list, company=company, exchange_date=exchange_date, **kwargs
        )
