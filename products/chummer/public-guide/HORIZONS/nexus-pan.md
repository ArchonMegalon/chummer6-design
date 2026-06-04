# NEXUS-PAN

Shared state survives device churn without the table losing trust.

![NEXUS-PAN horizon art](../assets/horizons/nexus-pan.png)

## Why this matters

My devices drift and the table loses confidence.

Picture the scene: A player reconnects in the middle of a session and gets back in step without the GM rebuilding everything by memory.


## Current stage

- Today: Shipped first-party continuity lane.
- Next: Flagship depth hardening.

## The problem

When phones, tablets, or laptops drift apart during play, the whole table stops trusting what is on screen.

## What it does now

Chummer keeps reconnects and shared session state steady enough that players can jump back in without the GM rebuilding context by hand.
It builds on the existing session record instead of creating a separate version of events.
It also handles bad signals and device handoffs honestly: clear offline status, safe local continuity, and visible conflict recovery when reconnecting goes wrong.

## What has to be true first

* durable session state
* reliable sync bundles
* visible reconnect explanations
* in-session reliability
* offline-capable local state
* explicit stale, pending, and conflicted state

## Current boundary

The live release still depends on boringly reliable session continuity.
Richer PAN behavior can expand from that base, but it cannot outrun reconnect honesty, offline posture, or visible conflict recovery.
