---
name: ticket-triage
description: CodeHub's specific escalation rules for classifying and routing support tickets
license: MIT
---

# CodeHub Ticket Triage Skill

## Escalation Rules

- **billing** + "twice"/"duplicate" -> priority `critical`, always offer a refund.
- **bug** + "crash"/"can't log in" -> priority `high`.
- Anything else -> priority `medium`, category `general`.

## Routing

Once classified, delegate to the matching subagent (`billing-specialist` or
`tech-specialist`) via the `task` tool -- don't answer billing/bug questions yourself.
