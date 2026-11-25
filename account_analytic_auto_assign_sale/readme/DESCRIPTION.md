Adds a **Project** (analytic account) to the sale order header. Every order
line gets it in its analytic distribution, merged with what the native
analytic distribution models already put there: only the plan of the project
is replaced, the other columns are kept.

The project is passed to the invoices of the order, see
`account_analytic_auto_assign_account_move`.
