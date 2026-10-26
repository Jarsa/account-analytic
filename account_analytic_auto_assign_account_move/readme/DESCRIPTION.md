Adds a **Project** (analytic account) to the header of invoices, bills and
journal entries. Every product line gets it in its analytic distribution,
merged with what the native analytic distribution models already put there:
only the plan of the project is replaced, the other columns are kept.

Credit notes and duplicates keep the project. The project can be used to
search and group invoices, and draft vendor bills without a project show a
warning.

This module is also the base of `account_analytic_auto_assign_sale` and
`account_analytic_auto_assign_purchase`, which pass the project of the order
to its invoices.
