---
title: Support Triage OpenEnv
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---
\# Support Triage OpenEnv

\*\*A Real-World Customer Support Environment\*\*



\## Motivation

Agents shouldn't just play games; they need to solve real business operations. This environment simulates a customer support ticketing queue where agents must read emails, assign the correct tags, assess priority, and draft responses. It directly models a genuine task used for evaluating agentic reliability in enterprise settings.



\## Action \& Observation Spaces

\* \*\*Action Space:\*\* `TriageAction` (ticket\_id, category, priority, reply\_draft)

\* \*\*Observation Space:\*\* `TriageObservation` (List of unresolved tickets, system messages, resolved count)



\## Tasks \& Difficulty

\* \*\*Easy:\*\* 1 obvious technical support ticket.

\* \*\*Medium:\*\* 3 tickets (mix of support, billing, and spam).

\* \*\*Hard:\*\* 5 tickets (vague descriptions, angry customers, high-priority routing).



\## Setup \& Baseline

1\. `docker build -t triage-env .`

2\. `docker run -p 8000:8000 triage-env`

3\. Set your `HF\_TOKEN` and run `python inference.py`.



Baseline uses Qwen2.5-72B-Instruct and reliably scores >0.85 on the Hard task.

