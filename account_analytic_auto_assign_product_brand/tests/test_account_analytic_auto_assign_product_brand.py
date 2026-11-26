# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountAnalyticAutoAssignProductBrand(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.brand = cls.env["product.brand"].create({"name": "Brand Test"})
        cls.product_a.product_brand_id = cls.brand
        brand_plan = cls.env["account.analytic.plan"].create({"name": "Brand Plan"})
        business_plan = cls.env["account.analytic.plan"].create(
            {"name": "Business Plan"}
        )
        cls.brand_account = cls.env["account.analytic.account"].create(
            {"name": "Brand Account", "plan_id": brand_plan.id}
        )
        cls.business_account = cls.env["account.analytic.account"].create(
            {"name": "Business Account", "plan_id": business_plan.id}
        )
        cls.env["account.analytic.distribution.model"].create(
            [
                {
                    "product_brand_id": cls.brand.id,
                    "analytic_distribution": {str(cls.brand_account.id): 100.0},
                },
                {
                    "product_categ_id": cls.product_a.categ_id.id,
                    "analytic_distribution": {str(cls.business_account.id): 100.0},
                },
            ]
        )

    def test_brand_merged_with_category(self):
        invoice = self.init_invoice("out_invoice", products=self.product_a)
        keys = invoice.invoice_line_ids.analytic_distribution
        self.assertEqual(len(keys), 1)
        key, percentage = next(iter(keys.items()))
        self.assertEqual(
            set(key.split(",")),
            {str(self.brand_account.id), str(self.business_account.id)},
        )
        self.assertEqual(percentage, 100.0)

    def test_product_without_brand(self):
        invoice = self.init_invoice("out_invoice", products=self.product_b)
        self.assertNotIn(
            str(self.brand_account.id),
            ",".join(invoice.invoice_line_ids.analytic_distribution or {}),
        )
