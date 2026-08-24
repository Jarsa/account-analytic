Adds a **Project** (analytic account) field to the sale order header. When
set, it applies to every order line and is carried over to the resulting
invoice automatically, without any recapture.

Unlike the other `account_analytic_auto_assign_*` modules, this one is not
about matching rules on master data — it is a direct, per-order choice
that merges with whatever other rules already apply (as long as the
project lives in its own analytic plan, which is the convention the rest
of this suite follows).
