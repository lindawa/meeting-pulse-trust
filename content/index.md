# Meeting Pulse: security & privacy

An overview for meeting participants, pilot users and stakeholders.

Meeting Pulse lets a person delegate attendance at selected Webex meetings and
receive relevant insights, keyword alerts and summaries. It supports the person;
it does not make decisions or commitments on their behalf.

## The essentials

- **Cisco on-premises hosting.** The current pilot application runs on
  Cisco-managed on-premises servers, not a public-cloud application host.
- **User-authorized access.** Delegations belong to the signed-in user's
  workspace. Connecting an assistant account does not grant access to someone
  else's meetings or give the assistant unlimited permission.
- **Protected connections.** The pilot uses HTTPS for its service entry point.
  Authorized services process meeting content; this is not a claim of
  cryptographic end-to-end encryption.
- **Encrypted production storage.** The deployment owner has confirmed that the
  production datastore is encrypted at rest and managed by the Cisco
  infrastructure team.
- **Participant awareness and control.** Obtain the required permission before
  use. Participants can ask for the assistant to be removed. Stopping it is
  different from deleting information already processed.
- **Human review.** Summaries and alerts can be incomplete or incorrect and need
  review before they are relied on or shared.

## A high-level view

[![Information flows between the user, Webex, the Cisco on-premises Meeting Pulse service, configured AI services and approved outputs. Hosting and AI-processing boundaries are separate.](assets/data-flow.svg)](assets/data-flow.svg)

The application hosting location does **not** establish the location or terms of
every supporting service. Webex, configured AI services and message delivery are
separate processing boundaries. The deployment owner must confirm which services
are permitted for a particular meeting's information.

## What this disclosure covers

This site explains the pilot's high-level data handling, user controls, technical
protections and limits on the assurances we can make. It contains no participant
records and does not provide access to the pilot application.

For the details that matter to you:

- [What information is processed, and why?](data-handling.html)
- [What does encryption protect?](security.html)
- [How do I control participation and sharing?](faq.html)
- [How do I raise a concern or request deletion?](support.html)

## About the assurance statements

This is project documentation, not an official Cisco Privacy Data Sheet, legal
notice, certification or replacement for an applicable agreement. A description
of a technical safeguard is not proof of formal security, privacy or Responsible
AI approval. Confirm the applicable deployment and approvals with the owner
before using sensitive information.
