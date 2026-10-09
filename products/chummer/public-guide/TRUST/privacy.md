# Your data, and how to leave

Local runner files stay local unless you choose a connected feature. Android Internal test builds with technical diagnostics enabled also send limited problem reports as described below. Chummer owns its retention and deletion policy; service providers do not. Hosted Build deletion claims stay review-gated until restore and whole-account erasure evidence passes.

## Technical problem reports, without your story

Internal builds that include automatic diagnostics enable sending by default, unless you have already switched it off. Reports help maintainers investigate failed actions, rejected UI updates and slow operations. They are not a record of everything you do, and a slow-operation report does not prove a crash.

- Each report contains the app version, observation time, app area, operation and outcome categories, duration, a general error category, and a random report ID for duplicate prevention. It contains no account or device identifier, runner or book text, credentials, screenshot, raw exception message or stack trace.
- Reports go over HTTPS to chummer.run. Like any web request, the connection exposes network metadata such as an IP address to hosting and network infrastructure; that metadata is not copied into the diagnostic report store.
- Individual reports expire after two days. The private receiver cleans them at startup and every 15 minutes while running. This short-lived store is separate from account history, support cases, Teable and backups. Maintainer alerts may contain technical categories and counts, not individual report IDs or user content.
- You can turn diagnostic sending off in the app settings at any time. This stops new sends, cancels pending delivery and clears unsent reports. Reports already accepted by the server remain subject to the two-day expiry. Your off setting survives app updates and restarts.
- Development and public builds do not enable this Internal-test default. An Internal build must not be promoted unchanged to a public track.

## Your account keeps sign-in, preferences, and help together

Your Chummer account keeps your basic profile, linked sign-in methods, device access, support history, and preferences together so you do not have to rebuild that history by hand.

## The download file is the same for everyone

When Chummer publishes a download, everyone gets the same file. Chummer does not build a private installer just for your account. If account linking is available, the account step is a short-lived code that reconnects a local copy back to your account.

## Short-lived sign-in access stays out of your account record

Short-lived third-party access stays on the machine or service using it. Your account keeps consent, help history, and access records, not passwords or access keys.

## Recognition should not force publicity

Participation and recognition remain optional layers. Private product use, private support, and a quiet account setup remain valid even while community pages exist.

## Deletion has a clock and an evidence gate

A verified deletion removes active data within 24 hours. Chummer-controlled content backups have a 30-day maximum, content-free replay tombstones last 35 days, and a content-free audit record may remain for 365 days. These windows become a public deletion promise only after restore and whole-account erasure evidence passes.
