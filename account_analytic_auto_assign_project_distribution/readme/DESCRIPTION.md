Adds a **Project Distribution** to the analytic account, to split a project
between other analytic plans (for example 60% branch A and 40% branch B).

When that account is set as the project of an invoice, sale order or
purchase order (see `account_analytic_auto_assign_account_move`), its lines
get that split, with the project in every row. The split replaces the plans
it touches; the other columns given by the analytic distribution models are
kept.
