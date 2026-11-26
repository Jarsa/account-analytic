# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountAnalyticAutoAssignProductCategory(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        categ_obj = cls.env["product.category"]
        cls.parent = categ_obj.create({"name": "Parent Test"})
        cls.child = categ_obj.create({"name": "Child", "parent_id": cls.parent.id})
        cls.grandchild = categ_obj.create(
            {"name": "Grandchild", "parent_id": cls.child.id}
        )
        cls.other = categ_obj.create({"name": "Other Test"})
        plan = cls.env["account.analytic.plan"].create({"name": "Business Plan"})
        cls.parent_account, cls.child_account = cls.env[
            "account.analytic.account"
        ].create(
            [
                {"name": "Parent Business", "plan_id": plan.id},
                {"name": "Child Business", "plan_id": plan.id},
            ]
        )
        cls.model_obj = cls.env["account.analytic.distribution.model"]
        cls.model_obj.create(
            {
                "product_categ_id": cls.parent.id,
                "analytic_distribution": {str(cls.parent_account.id): 100.0},
            }
        )

    def _distribution(self, category):
        return self.model_obj._get_distribution(
            {"product_categ_id": category.id, "company_id": self.env.company.id}
        )

    def test_subcategory_inherits_parent_model(self):
        self.assertEqual(
            self._distribution(self.grandchild),
            {str(self.parent_account.id): 100.0},
        )

    def test_closest_category_wins(self):
        self.model_obj.create(
            {
                "product_categ_id": self.child.id,
                "analytic_distribution": {str(self.child_account.id): 100.0},
            }
        )
        self.assertEqual(
            self._distribution(self.grandchild), {str(self.child_account.id): 100.0}
        )
        self.assertEqual(
            self._distribution(self.parent), {str(self.parent_account.id): 100.0}
        )

    def test_unrelated_category(self):
        self.assertFalse(self._distribution(self.other))

    def test_invoice_line(self):
        self.product_a.categ_id = self.grandchild
        invoice = self.init_invoice("out_invoice", products=self.product_a)
        self.assertEqual(
            invoice.invoice_line_ids.analytic_distribution,
            {str(self.parent_account.id): 100.0},
        )
