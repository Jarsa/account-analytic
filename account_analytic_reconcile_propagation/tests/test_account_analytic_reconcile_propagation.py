# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountAnalyticReconcilePropagation(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_currency = cls.setup_other_currency("EUR")
        plan = cls.env["account.analytic.plan"].create({"name": "Plan Test"})
        cls.account_a, cls.account_b = cls.env["account.analytic.account"].create(
            [
                {"name": "A", "plan_id": plan.id},
                {"name": "B", "plan_id": plan.id},
            ]
        )

    def _invoice(self, currency, invoice_date):
        invoice = self.init_invoice(
            "out_invoice",
            invoice_date=invoice_date,
            products=self.product_a + self.product_b,
            currency=currency,
        )
        line_a, line_b = invoice.invoice_line_ids
        line_a.write(
            {
                "price_unit": 300.0,
                "analytic_distribution": {str(self.account_a.id): 100},
            }
        )
        line_b.write(
            {
                "price_unit": 100.0,
                "analytic_distribution": {str(self.account_b.id): 100},
            }
        )
        invoice.invoice_line_ids.tax_ids = False
        invoice.action_post()
        return invoice

    def _assert_weighted(self, line):
        self.assertEqual(
            line.analytic_distribution,
            {str(self.account_a.id): 75.0, str(self.account_b.id): 25.0},
        )

    def test_exchange_difference_takes_invoice_distribution(self):
        invoice = self._invoice(self.other_currency, "2016-01-01")
        self._register_payment(invoice, payment_date="2017-01-01")
        exchange_move = invoice.line_ids.matched_credit_ids.exchange_move_id
        self.assertTrue(exchange_move)
        exchange_line = exchange_move.line_ids.filtered(
            lambda line: line.account_id.internal_group in ("income", "expense")
        )
        self._assert_weighted(exchange_line)

    def test_write_off_takes_invoice_distribution(self):
        invoice = self._invoice(self.company_data["currency"], "2017-01-01")
        writeoff_account = self.company_data["default_account_expense"]
        payment = self._register_payment(
            invoice,
            amount=380.0,
            payment_difference_handling="reconcile",
            writeoff_account_id=writeoff_account.id,
            writeoff_label="Discount",
        )
        writeoff_line = payment.move_id.line_ids.filtered(
            lambda line: line.account_id == writeoff_account
        )
        self._assert_weighted(writeoff_line)

    def test_no_invoice_distribution(self):
        self.assertFalse(
            self.env["account.move"]._get_reconcile_analytic_distribution()
        )
