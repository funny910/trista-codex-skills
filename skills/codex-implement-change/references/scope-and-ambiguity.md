# Scope and ambiguity

Use this reference when an unresolved choice could change behavior, compatibility, data, security, or meaningful cost.

## Material ambiguity

A choice is materially ambiguous when multiple plausible interpretations remain and choosing among them would change any of:

- public or caller-visible behavior, API shape, or compatibility;
- persisted data, migration semantics, security, or privacy;
- meaningful operational cost or the repository area authorized for change.

## Safe assumptions

Resolve minor, reversible implementation details from repository evidence such as tests, types, documentation, callers, and established local conventions. State an assumption when it affects how the result should be interpreted.

## Exact stop rule

If repository evidence does not select one option and two or more plausible options would differ materially, do not edit. Ask the user to choose, naming the options and their concrete impact. Do not choose merely because one option is conventional or quicker.
