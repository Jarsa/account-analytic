# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountAnalyticAutoAssignProjectDistribution(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        plan_obj = cls.env["account.analytic.plan"]
        account_obj = cls.env["account.analytic.account"]
        project_plan = plan_obj.create({"name": "Project Plan Test"})
        branch_plan = plan_obj.create({"name": "Branch Plan Test"})
        brand_plan = plan_obj.create({"name": "Brand Plan Test"})
        cls.branch_a = account_obj.create({"name": "A", "plan_id": branch_plan.id})
        cls.branch_b = account_obj.create({"name": "B", "plan_id": branch_plan.id})
        cls.branch_c = account_obj.create({"name": "C", "plan_id": branch_plan.id})
        cls.brand = account_obj.create({"name": "Brand", "plan_id": brand_plan.id})
        cls.project = account_obj.create(
            {
                "name": "Split Project",
                "plan_id": project_plan.id,
                "analytic_distribution": {
                    str(cls.branch_a.id): 60.0,
                    str(cls.branch_b.id): 40.0,
                },
            }
        )
        cls.plain_project = account_obj.create(
            {"name": "Plain Project", "plan_id": project_plan.id}
        )
        cls.env["account.analytic.distribution.model"].create(
            {
                "product_id": cls.product_a.id,
                "analytic_distribution": {
                    f"{cls.branch_c.id},{cls.brand.id}": 100.0,
                },
            }
        )

    def _distribution(self, project):
        invoice = self.init_invoice("out_invoice", products=self.product_a)
        invoice.analytic_account_id = project
        return invoice.invoice_line_ids.analytic_distribution

    def _key(self, *accounts):
        return ",".join(str(account.id) for account in sorted(accounts, key=int))

    def _normalize(self, distribution):
        return {
            ",".join(sorted(key.split(","), key=int)): value
            for key, value in distribution.items()
        }

    def test_project_split_replaces_branch_and_keeps_brand(self):
        self.assertEqual(
            self._normalize(self._distribution(self.project)),
            {
                self._key(self.project, self.branch_a, self.brand): 60.0,
                self._key(self.project, self.branch_b, self.brand): 40.0,
            },
        )

    def test_project_without_split(self):
        self.assertEqual(
            self._normalize(self._distribution(self.plain_project)),
            {self._key(self.plain_project, self.branch_c, self.brand): 100.0},
        )
