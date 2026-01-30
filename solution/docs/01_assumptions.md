# Assumptions and Decisions

## Base Assumptions (check and revise)
- [ ] Season method split: seasons 1-2 rank, seasons 3-27 percent, seasons 28-34 rank + judge save.
- [ ] Fan votes are modeled as weekly shares; absolute totals are not identifiable.
- [ ] Fan vote shares are nonnegative and sum to 1 each week.
- [ ] Fan vote shares vary smoothly week-to-week for the same contestant (regularization).
- [ ] Weeks with no elimination still provide valid scoring data.
- [ ] Weeks with multiple eliminations remove the lowest k combined scores.
- [ ] Judges save: bottom two identified by combined scores; judges eliminate lower judge_total.
- [ ] Zero scores after elimination indicate non-participation (exclude from modeling after exit).
- [ ] N/A score entries are treated as missing, not zeros.

## Alternatives to Test
- [ ] Judge save rule: judges choose higher total to save vs separate judge vote model.
- [ ] Weighting of judge vs fan influence (50/50 vs calibrated).
- [ ] Include popularity covariates (age, industry, home region, pro dancer).

## Open Questions
- Exact season when rank method returned (assume season 28 unless evidence).
- Whether judge save was used every week after season 28.
- Treatment of team dances and bonus points (use provided scores as-is).

## Logging Format (append new entries)
```
YYYY-MM-DD
Decision:
Reason:
Impact:
Alternatives considered:
```
