# Common questions

## What is Meeting Pulse for?

It helps you stay on top of selected Webex meetings when time zones or overlapping
commitments prevent you from attending. Your chosen persona shapes the insights,
summaries and action items, while configured keyword alerts highlight moments
that may need your attention. You can follow up or step into a discussion when
needed; the assistant does not make decisions or commitments for you.

## Does the assistant contribute on my behalf?

It helps you recognize when your input may be needed, so you can decide how to
respond. Receiving an alert is not the same as the assistant speaking, approving
a decision or making a commitment on your behalf.

## Where is the pilot application hosted?

On Cisco-managed on-premises servers, not a public-cloud application host.
Webex, configured AI services and delivery channels have separate hosting and
processing boundaries.

## Does a public documentation site make my meeting information public?

No. This site contains project documentation, not meeting records, and it does
not grant access to the pilot application.

## Is the information encrypted end to end?

The pilot uses encrypted transport at its service entry. This is not the same as
cryptographic end-to-end encryption: authorized application and AI services
process content to provide the requested insights.

## Is all stored information encrypted?

For the current pilot, the deployment owner has confirmed that the production
datastore is encrypted at rest and managed by the Cisco infrastructure team.
Stored Webex access credentials and configured AI-provider secrets are encrypted
before storage as an additional safeguard. Authorized services and database
queries can still return readable meeting records; datastore encryption does
not mean every transcript field has separate application-level encryption.
This does not establish identical
protection for copies exported elsewhere, external backups, delivered messages
or AI-provider records; those boundaries must be assessed separately.

## Does Meeting Pulse require a Webex recording?

Not in every case. Available captions or received meeting audio can supply
meeting information. Shared-screen context may also be enabled. Recording,
transcription and assistant processing are different activities.

## If I turn transcription off, does the assistant stop listening?

Do not assume so. Audio fallback can remain available. To stop participation,
ask for the assistant to leave or have the host remove it, then verify departure.

## How are participants informed?

The person delegating the meeting is responsible for obtaining the required
permission and providing notice. The application supports attendance notices;
Webex's display can vary by participation mode and may group connections under
one identity. Do not rely solely on a separate bot entry as evidence of notice.

## Can I decline or ask for the assistant to leave?

Yes. Tell the delegating user or meeting host. The host can use Webex participant
controls to remove the assistant connection where available. Confirm that it has
left rather than treating a pending leave request as completion.

## Can other pilot users see my meetings?

Normal application access is restricted to the signed-in user's workspace.
Authorized operators, configured AI services and approved output recipients are
separate access considerations; workspace separation is not a zero-access claim.

## Who receives keyword alerts and summaries?

The delivery depends on the user's saved and meeting-specific settings. Review
configured subscribers before delegation and ensure each recipient is appropriate
for the meeting information.

## Does linking MyAgent give it unrestricted access?

No. Linking associates the authenticated identity with the matching account and
approved permissions. It does not grant access to another person's workspace or
replace the need for permission to perform a requested action.

## Do I need to share my Webex password?

No. Sign in through the Webex sign-in flow. Do not send passwords, access tokens
or account-connection links to other people or paste them into a chat.

## Is meeting information used to train AI models?

Do not assume the same answer for every configurable provider. Confirm the
approved provider, contract, data-use settings and retention terms with the
deployment owner. This project disclosure does not make a universal no-training
assurance.

## Which AI services does the Cisco-managed pilot use?

The deployment owner confirms use of Cisco-approved enterprise AI services,
including Circuit and CX AI services as configured for the pilot. Approval
depends on the actual service, model, use case and permitted data classification.
It is not a blanket approval of every custom provider or consumer account from
the same model vendor.

## Does that guarantee no PII reaches an AI service?

No universal guarantee is made. PII means personally identifiable information,
which can include names or contact details appearing in meeting content.
Platform screening can reduce exposure, but its coverage and API path must be
verified. Approved processing and restrictions on model training are different
from a guarantee that no personal information is ever processed.

## Does on-premises hosting mean information never leaves those servers?

No. Webex participation, configured AI processing and message delivery are
separate data flows. The approved configuration determines which services
receive information and what rules apply.

## Does logging out stop a running delegate?

Do not rely on logout as a stop control. Use the delegation's leave controls or
ask the host to remove the assistant. Confirm that the assistant has left.

## Does stopping the assistant delete its notes?

No. Stopping new participation and deleting previously processed information are
separate actions. Records, delivered messages, backups and provider-side copies
can require different handling.

## How long is meeting information kept?

Ask for the deployment's effective retention policy. This disclosure does not
promise a universal automatic deletion deadline. A retention preference alone
does not establish deletion across all systems and copies.

## Can I request deletion or a copy of information?

Yes. Contact the deployment owner through the private support channel, identify
the meeting and information involved, and ask what can be provided or removed.
Applicable access, retention and contractual requirements still apply. Do not
post private meeting details in a public GitHub issue.

## What information is collected for usage monitoring?

Usage monitoring can record activity and reliability information without meeting
content in the analytics events. Pseudonymous identifiers are not necessarily
anonymous. Operational records can also contain identifiers and must be handled
as service data.

## Is feedback private, and can it include a screenshot?

Feedback may be stored for support and notified to the configured support owner.
Optional diagnostics and screenshots can contain identifying or sensitive
information. Remove secrets and unnecessary personal or customer information
before submitting them.

## Is the assistant always accurate?

No. Captions, audio fallback, speaker attribution and AI interpretation can all
be imperfect. Treat outputs as assistance and review important information before
acting or sharing it.

## Has this page established formal security or privacy approval?

No. A technical description is not an approval record or official Privacy Data
Sheet. Ask the deployment owner for the actual review scope and evidence that
apply to the intended use.
