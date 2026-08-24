Central engine for automatic analytic account assignment.

Odoo already ships a native engine (`account.analytic.distribution.model`)
that automatically matches the analytic distribution of invoices, sales,
purchases and expenses by customer, contact tag, company, product, product
category and account code prefix. Its limitation: when two rules touch the
same analytic plan, only the first one found (by `sequence`) is applied
and the rest of that rule is discarded, even if it also covered another
plan without any conflict.

This module adds its own engine (`account.analytic.auto.assign.rule`)
that does merge several sources at once (product, category, customer,
account prefix...), designed so that each business source (project,
operating unit, product line, brand) lives in its own analytic plan and
therefore never competes with the others.

**The custom engine only kicks in when there is no record at all in
Accounting > Configuration > Analytic > Analytic Distribution Models.**
It is a global switch: if the business decides to use Odoo's native
rules, they are respected as-is and this module does not interfere.
