# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from odoo.addons.account_analytic_auto_assign_operating_unit.tests import (
    test_account_analytic_auto_assign_operating_unit as ou_test,
)


@tagged("post_install", "-at_install")
class TestAccountAnalyticAutoAssignSaleOperatingUnit(
    ou_test.TestAccountAnalyticAutoAssignOperatingUnit
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.group_ids |= cls.env.ref("sales_team.group_sale_manager")

    def test_sale_line(self):
        order = self.env["sale.order"].create(self._order_vals(self.unit_a))
        self.assertEqual(
            order.order_line.analytic_distribution, {str(self.account_a.id): 100.0}
        )
        order.operating_unit_id = self.unit_b
        self.assertEqual(
            order.order_line.analytic_distribution, {str(self.account_b.id): 100.0}
        )
