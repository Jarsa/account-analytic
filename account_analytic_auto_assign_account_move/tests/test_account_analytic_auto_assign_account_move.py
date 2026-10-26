# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountAnalyticAutoAssignAccountMove(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project_plan = cls.env["account.analytic.plan"].create(
            {"name": "Project Plan Test"}
        )
        cls.branch_plan = cls.env["account.analytic.plan"].create(
            {"name": "Branch Plan Test"}
        )
        cls.project = cls.env["account.analytic.account"].create(
            {"name": "Project Test", "plan_id": cls.project_plan.id}
        )
        cls.other_project = cls.env["account.analytic.account"].create(
            {"name": "Other Project Test", "plan_id": cls.project_plan.id}
        )
        cls.branch = cls.env["account.analytic.account"].create(
            {"name": "Branch Test", "plan_id": cls.branch_plan.id}
        )
        cls.env["account.analytic.distribution.model"].create(
            {
                "product_id": cls.product_a.id,
                "analytic_distribution": {str(cls.branch.id): 100.0},
            }
        )

    def _key(self, *accounts):
        return ",".join(str(account.id) for account in sorted(accounts, key=int))

    def _normalize(self, distribution):
        return {
            ",".join(sorted(key.split(","), key=int)): value
            for key, value in distribution.items()
        }

    def _invoice(self, move_type="out_invoice", project=None):
        invoice = self.init_invoice(move_type, products=self.product_a)
        invoice.analytic_account_id = project
        return invoice

    def test_project_merged_with_distribution_models(self):
        invoice = self._invoice(project=self.project)
        self.assertEqual(
            self._normalize(invoice.invoice_line_ids.analytic_distribution),
            {self._key(self.project, self.branch): 100.0},
        )

    def test_changing_project_replaces_only_its_plan(self):
        invoice = self._invoice(project=self.project)
        invoice.analytic_account_id = self.other_project
        self.assertEqual(
            self._normalize(invoice.invoice_line_ids.analytic_distribution),
            {self._key(self.other_project, self.branch): 100.0},
        )

    def test_without_project_keeps_native_behavior(self):
        invoice = self._invoice()
        self.assertEqual(
            invoice.invoice_line_ids.analytic_distribution,
            {str(self.branch.id): 100.0},
        )

    def test_credit_note_keeps_project(self):
        invoice = self._invoice(project=self.project)
        invoice.action_post()
        reversal = (
            self.env["account.move.reversal"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create({"journal_id": invoice.journal_id.id})
        )
        credit_note = self.env["account.move"].browse(reversal.refund_moves()["res_id"])
        self.assertEqual(credit_note.analytic_account_id, self.project)
