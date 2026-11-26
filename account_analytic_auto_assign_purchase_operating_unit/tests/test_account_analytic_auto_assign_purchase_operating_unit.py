# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from odoo.addons.account_analytic_auto_assign_operating_unit.tests import (
    test_account_analytic_auto_assign_operating_unit as ou_test,
)


@tagged("post_install", "-at_install")
class TestAccountAnalyticAutoAssignPurchaseOperatingUnit(
    ou_test.TestAccountAnalyticAutoAssignOperatingUnit
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.group_ids |= cls.env.ref("purchase.group_purchase_manager")

    def test_purchase_line(self):
        order = self.env["purchase.order"].create(self._order_vals(self.unit_b))
        self.assertEqual(
            order.order_line.analytic_distribution, {str(self.account_b.id): 100.0}
        )
