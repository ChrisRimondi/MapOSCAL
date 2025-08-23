---
layout: post
title: "Downshifting Compliance - Embedding Compliance into Platform Abstractions"
date: 2025-08-23 10:00:00 -0600
description: "Why compliance should 'shift down' into platforms."
tags: [Platform Engineering, OSCAL, Open Source, Compliance, Cybersecurity, JSON, DevTools, automation, DevOps, SRE, SSP]
categories: updates
---

# **Shifting Down: Embedding Compliance into Platform Abstractions**

Engineering teams constantly balance efficiency, quality, and cost, all while delivering value to customers. Compliance is often treated as something bolted on at the end of the process, creating overhead and slowing teams down.

But there’s a better way. In a recent talk from Google at PlatformCon 2025, they emphasized the idea of **“shift down”**: 

> Shift down is an approach that advocates for embedding decisions and responsibilities into underlying internal developer platforms (IDPs), thereby reducing the operational burden on developers. This contrasts with the DevOps trend of "shift left," which pushes more effort earlier into the development cycle, a method that is proving difficult at scale due to the sheer volume and rate of change in requirements.

We think this type of thinking applies equally in the compliance space.

---

## **The Compliance Leverage of Platforms**

When we analyzed a System Security Plan (SSP), one insight stood out: **not all components are equal when it comes to compliance leverage.**

Some parts of the stack contribute far more to compliance than others. For example:

* A Kubernetes **Ingress Controller** that enforces TLS and mTLS delivers massive compliance leverage.
* A service mesh that ensures **zero-trust networking** applies to every workload without extra developer effort.
* A hardened base image contributes compliance to all workloads built on top of it.

Contrast that with individual app teams rolling their own TLS logic. It’s inefficient, inconsistent, and hard to audit.

---

## **OSCAL as a Modeling Tool**

This is where OSCAL comes in. Within the OSCAL Component Definition model:

* **Components** represent discrete systems or services (e.g., “Kubernetes Ingress Controller”).
* **Capabilities** are reusable compliance functions that span multiple components (e.g., “Terminate ingress TLS with mTLS to backends”).

By modeling both, OSCAL gives you a map of **where compliance actually lives in your stack.**

---

## **Shifting Down with Capabilities**

Capabilities can hold the *primary* implementation of cross-cutting controls. Workloads can then reference—or inherit—these implementations instead of duplicating them.

* Example:

  * Capability: “All ingress TLS is terminated by the Ingress Controller with mTLS to backends.”
  * Workloads: Simply depend on this capability; they don’t need their own custom TLS implementation.

This reduces duplication, ensures consistency, and makes audits simpler.

---

## **Case Study: Compliance Inheritance**

Imagine a simple stack:

* **Platform layer**: Istio Service Mesh implements mTLS for all services.
* **Workload layer**: Applications only need to integrate with the mesh.

In OSCAL:

* The platform component definition describes the mTLS capability.
* Application component definitions reference that capability.

Compliance evidence is tied to the platform once—not re-documented for every workload.

---

## **Visual Framework: Compliance Leverage by Abstraction Layer**

Here’s how different layers of abstraction compare in terms of compliance leverage:

![Compliance Leverage Diagram](sandbox:/mnt/data/compliance_leverage.png)

---

## **Why This Matters**

For engineering teams:

* Reduced toil and duplicate work.
* Compliance becomes part of the developer experience.
* Faster delivery without sacrificing quality.

For compliance teams:

* Clear responsibility boundaries in SSPs.
* Easier evidence collection and audits.
* Stronger posture by enforcing controls at the right layer.

---

## **Conclusion**

Shifting compliance down into platforms is more than a compliance strategy — it’s an engineering acceleration strategy.

The question to ask: *Where in your stack should compliance primitives live?*

By using OSCAL to model components and capabilities, teams can visualize these leverage points, reduce wasted effort, and deliver both faster and safer.


---

*Authored by [Chris Rimondi](https://www.linkedin.com/in/crimondi/)*
