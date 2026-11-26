# How meeting information is handled

The purpose of processing is to provide the meeting coverage, alerts and insights
that an authorized user requests. Only use Meeting Pulse where the meeting's
participants, information classification and applicable policies permit it.

## Information that can be processed

| Information | Why it is needed |
| --- | --- |
| Account identity and preferences | Associate activity with the correct user, apply settings and support account access. |
| Meeting details and participant information | Identify the selected meeting, schedule attendance and provide context. |
| Captions, transcript text or received meeting audio | Understand the discussion and produce requested insights. Available sources depend on the meeting and deployment. |
| Shared-screen context, when enabled | Interpret relevant information shown during the meeting. Do not share sensitive material unnecessarily. |
| Summaries, action items, alerts and saved subscriber settings | Provide relevant updates and later review. |
| Feedback and optional diagnostics | Investigate a user-submitted issue. Free text and screenshots can contain sensitive information. |
| Usage and operational records | Understand adoption, reliability and service health. These records are not necessarily anonymous. |

## Hosting and processing boundaries

The current pilot application is hosted on **Cisco-managed on-premises servers**.
That statement applies to application hosting, not automatically to every
supporting service or AI model.

Meeting information can pass through Webex, the application, a configured AI
service and the chosen delivery channel. Depending on the feature, an AI request
can include meeting text, shared-content context and the instructions needed to
produce a personalized result.

An on-premises application does not, by itself, guarantee that all processing
stays on premises or that information never reaches another service. Confirm
approved providers, processing locations, retention terms and permitted data
classifications with the deployment owner.

## Capture is not the same as Webex recording

Meeting Pulse can use available Webex captions and can fall back to processing
received meeting audio. Shared-screen context is a separate option.

**Turning off Webex recording or transcription must not be treated as a universal
stop-capture control for Meeting Pulse.** Ask for the assistant to leave or have
the host remove it, and confirm that participation has ended.

## Access and sharing

Normal application access is scoped to the signed-in user's workspace. That does
not mean a meeting's information can never be accessed by an authorized service
operator, processed by a configured AI service or delivered to a configured
recipient.

Review alert recipients and delivery settings before delegating a meeting. An
alert or summary may itself contain sensitive information. Copies delivered to
messaging systems, downloaded by a user or copied elsewhere have separate access
and retention controls.

## Protection of stored information

The deployment owner has confirmed that the current pilot's production datastore
is encrypted at rest and managed by the Cisco infrastructure team. Authorized
application services still process meeting information to provide the requested
capabilities.

This storage assurance does not automatically extend to copies exported elsewhere,
delivered messages or AI-provider records. Their protections and retention need
to be confirmed separately.

## Retention and deletion

Do not assume a displayed retention preference guarantees automatic removal of
all meeting information. A universal, verified automatic meeting-content deletion
deadline is not asserted by this disclosure.

Ask the deployment owner for the effective retention policy covering active
records, operational records, backups, AI providers and delivered copies. A
request must identify which information and systems it concerns. Leaving a
meeting, logging out or disconnecting an integration does not itself erase
previously processed information.

See [support and privacy requests](support.html) for the private request process.
