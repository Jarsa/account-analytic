Extends `account_analytic_auto_assign` so its rules can also match by
**product brand**, driven by a required analytic account field directly on
the brand, instead of a rule created by hand.

Covers invoices/bills, sale orders, purchase orders and expenses.

`sale.order.line`, `purchase.order.line` and `hr.expense` do not expose an
overridable "get matching arguments" method the way `account.move.line`
does, so this module's overrides of their compute call `super()` first and
only layer their own contribution on top, instead of rebuilding the field
from scratch — this lets other sibling modules extending the same compute
(for example `account_analytic_auto_assign_operating_unit` on sale orders)
compose correctly regardless of install order.
