# Protection and assurance boundaries

Security depends on the application, its deployment and the supporting services
used for a meeting. These boundaries matter more than a blanket assurance.

## Cisco on-premises application hosting

The current pilot application runs on Cisco-managed on-premises servers. Access
to the pilot remains controlled; making this documentation public does not make
the application or its meeting records public.

The hosting statement is not a claim about the physical location of Webex,
configured AI processing or every delivery service. Those services must be
assessed separately for the intended information.

## Encryption in transit

The pilot's public-facing service entry uses HTTPS with a trusted certificate.
Configured service connections must also meet the deployment's security policy.

Encryption in transit protects information while it crosses a protected
connection. The application and configured AI services still need to process
meeting content to create insights. This is **not cryptographic end-to-end
encryption** in which only meeting participants can decrypt the content.

## Encryption and protection at rest

The deployment owner has confirmed that the current pilot's **production datastore
is encrypted at rest**, with the datastore managed by the **Cisco infrastructure
team**. This is an infrastructure protection for stored information, in addition
to the application's controls.

Meeting information stored within that datastore is protected by this
encryption-at-rest layer. Authorized application services and database access
can still retrieve readable records; this is not a claim that each transcript
field has separate application-level encryption or that the service cannot read
it.

Stored Webex access credentials and configured AI-provider secrets are encrypted
before storage. Encryption does not remove the need for access controls: authorized
services must be able to process content, and privileged infrastructure access
remains an operational responsibility.

Do not extend the production-datastore assurance to every exported copy, external
backup location, delivered message or AI-provider record. Confirm the safeguards
and retention that apply to those separate copies with the deployment owner.

## Identity, authorization and consent

- The signed-in identity determines the user's workspace; normal users do not
  receive unrestricted access to other users' records.
- Integration access is scoped, and connecting an account requires the user's
  explicit approval. The integration identity must match the account being linked.
- Account-link consent is not the same as permission from meeting participants.
  Obtain any required meeting permission before delegation.
- Access to a capability does not authorize every action it can perform. Ask for
  a specific action and review the confirmed result.

## Responsible AI and approved services

The deployment owner confirms that the Cisco-managed pilot uses Cisco-approved
enterprise AI services, including Circuit and CX AI services as configured for
the deployment. These are enterprise service arrangements, not permission to
send meeting information to any public chatbot or arbitrary provider endpoint.
The approved model, use case and data classification still matter, including
when a fallback provider is used.

[Cisco's Responsible AI Framework](https://www.cisco.com/c/dam/en_us/about/doing_business/trust-center/docs/cisco-responsible-artificial-intelligence-framework.pdf)
sets out transparency, fairness, accountability, privacy, security and
reliability as its principles and calls for relevant AI use-case assessments.
Meeting Pulse's responsible-use approach emphasizes participant awareness,
account-scoped access, appropriate recipients and human review. Using an approved
AI platform supports that approach; it does not by itself complete the separate
review of this application or its meeting use case.

## Personal information and AI processing

Cisco [describes privacy screening and security guardrails in its internal AI
assistant](https://blogs.cisco.com/cisco-on-cisco/cisco-secure-internal-ai-assistant).
Those platform safeguards must not be read as a guarantee that every piece of
personal information is removed from every Meeting Pulse request. Meeting text
and enabled shared-content context can include names or other personal
information, and screening coverage depends on the selected service and route.

Minimize unnecessary personal information and use only services and meeting data
permitted for the intended purpose. Do not assume that "Cisco-approved," "not
used for model training" and "no personal information is processed" mean the
same thing. Confirm the actual service's processing and data-use terms.

## AI output and human responsibility

AI output can omit context, misidentify a speaker or generate an incorrect
interpretation. Review important decisions, action owners and customer-facing
communications against the underlying meeting context.

The project's technical safeguards do not establish a universal no-training
promise across configurable AI providers. Provider selection, contractual terms,
data-use settings and retention must be confirmed for the actual deployment.

## Assurance status

This site describes technical behavior and its boundaries. It does not claim
completed CSDL, DGSPA, Responsible AI, legal or independent security certification
without the corresponding review evidence. Consult the deployment owner for the
current approval scope, permitted data classifications and any use restrictions.

Do not infer general availability, suitability for every sensitive meeting, or a
guaranteed service level from participation in the pilot.
