# Public Privacy and Account Lifecycle

Public Chummer surfaces must explain what is stored, what is not, and how users can leave safely.

## Authority

Chummer owns this policy. The project owner is the single accountable product
authority and may update it through a reviewed, versioned repository change.
Hosting, identity, email, AI, storage, and marketplace providers are processors
or delivery adapters. Their dashboards, defaults, receipts, and terms do not
become Chummer account, retention, deletion, release, or campaign truth.

No second company, review board, or invented multi-role committee is required
to choose Chummer's product policy. Implementation and release proof remain
separate: an owner-approved sentence is not evidence that a deletion or restore
path works.

## Minimum posture

- public feedback stays separate from private support, crash, and account lanes
- linked identities and recovery surfaces redact sensitive labels by default
- deletion, export, retention, and support follow-up posture must be named before public launch
- private logs, campaign spoilers, and copyrighted rules text are never valid public submissions
- install and account recovery surfaces must stay first-party and receipt-backed

## Account and Hosted Build policy

The public account and Hosted Build lifecycle uses these maximum windows:

| Data | Active use | After workspace or account deletion |
| --- | --- | --- |
| Active account and Hosted Build rows | While the account or workspace remains active | Remove from serving surfaces immediately and delete from the active store within 24 hours. |
| Chummer-controlled content-bearing database backups and point-in-time recovery data | Disaster recovery only | Expire within 30 days. A deletion journal must be replayed before restored data can be served. |
| Content-free deletion tombstones and replay journal | Not used as product content | Retain for 35 days after deletion, then purge. Tombstones may contain keyed owner/workspace identifiers, revision, time, and receipt digest, but no character, campaign, support, or free-text content. |
| Content-free deletion audit receipt | Not used as product content | Retain for 365 days so Chummer can prove that the request was handled; do not retain the deleted payload. |
| Operational logs | Up to 30 days | Redact secrets and content; delete on the same clock unless a shorter security incident window applies. |

Downloaded files and copies a user shared outside Chummer are outside Chummer's
custody. The deletion flow must say that plainly.

## Deletion behavior

Workspace deletion must atomically write a content-free tombstone and remove the
active row. Creating the same owner/workspace lineage stays blocked until the
35-day tombstone expires. Restore and failover procedures must apply the current
deletion journal before opening the serving store, so older backup bytes cannot
resurrect a deleted workspace.

Account deletion must:

1. verify the signed-in owner;
2. revoke active sessions, device links, and pending account grants;
3. hide the account and its Hosted Build data immediately;
4. delete active account, workspace, campaign-membership, private support, and
   provider-routing records within 24 hours, except records that must be reduced
   to a content-free deletion receipt;
5. keep deletion replay effective for the 30-day backup window;
6. purge the replay tombstone after day 35 and keep only the content-free
   365-day audit receipt.

Chummer has no ordinary legal-hold mode. If law requires preservation, the
project owner must record the exact scope and basis, restrict access, preserve
only the required data, and tell the user unless legally prohibited. A provider
default or an open support case is not a legal hold.

## Release proof

Public deletion claims stay blocked until tests and operator evidence prove:

- workspace delete, retry, conflict, and same-lineage recreation fencing;
- owner-wide erasure across Hub and Hosted Build stores;
- a restore from a pre-deletion backup followed by deletion-journal replay;
- 30-day backup, 35-day tombstone, 365-day receipt, and 30-day log cleanup;
- live privacy and account-deletion routes using the same policy version;
- a signed-in request completing without a support-only or email-only fallback.
