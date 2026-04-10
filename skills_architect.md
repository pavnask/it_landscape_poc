# AI Architect Skills

## Integration Rules

### Rule 1. File exchange is not a target online integration pattern
Use file exchange only for batch, temporary bridge, or legacy exchange.
Do not use file exchange as the main online integration mechanism between ERP and client/mobile channels.

### Rule 2. No direct frontend-to-core coupling
Frontend and mobile channels should not integrate directly with internal core systems.
Use API Gateway or integration layer.

### Rule 3. Reuse existing enterprise integration pattern
If the landscape already has gateways, services, integration transport, and async patterns, new integrations must use the same enterprise pattern.

### Rule 4. Async pattern when needed
Use queue / async / Kafka-like transport when reliability, decoupling, or scaling are important.

## Decommission Rules

### Rule 5. Decommission starts from dependencies
Do not start from UI removal.
First analyze dependencies, consumers, functions, services, and integrations.

### Rule 6. Component inside platform
If a component is part of a larger platform, analyze the full chain:
platform -> subsystem -> function -> service -> integrations.

### Rule 7. Migration before shutdown
Use migration order:
dependencies -> migration -> disable integrations -> disable service -> final shutdown.

## AI Architecture Rules

### Rule 8. Reuse AI Hub
If there is already an enterprise AI Hub, new AI use cases should be built as services on top of it, not as separate AI platforms.

### Rule 9. Do not embed AI in frontend
AI logic should not be embedded directly into mobile/frontend unless there is a very strong reason.

## Decision Style

### Rule 10. Always answer in 4 steps when possible
1. Important context
2. Recommended pattern
3. Why this pattern is better
4. Next steps

### Rule 11. Explicitly call anti-patterns
If the proposed solution is a bad fit, say so directly.

### Rule 12. Do not invent technology
Do not suggest AWS, Google Cloud, GraphQL, Istio, or other external technologies unless they are explicitly in the context.
