---
layout: post
title: "Downshifting Compliance"
date: 2025-09-01 10:00:00 -0600
description: "MapOSCAL Kubernetes Support"
tags: [Platform Engineering, OSCAL, Open Source, Compliance, Cybersecurity, JSON, DevTools, automation, DevOps, SRE, Kubernetes, K8s]
categories: updates
---

Here’s a draft blog post you could publish to highlight the **Kubernetes analysis** work in MapOSCAL v0.5.0. I went beyond a changelog and framed it around the design thinking behind the workload grouping and how it plays out in OSCAL component definitions.

---

# **Kubernetes Analysis in MapOSCAL v0.5.0**

We’ve just released [MapOSCAL v0.5.0](https://github.com/ChrisRimondi/MapOSCAL/releases/tag/v0.5.0), and this release takes a big step forward: **Kubernetes analysis**. While earlier versions of MapOSCAL focused on individual services or files, this update lets us reason about workloads at the cluster level and represent them as OSCAL components.

## Why Kubernetes Analysis Matters

Modern applications are rarely just one binary or container. They run as **collections of pods, deployments, and services**, stitched together into an ecosystem. From a compliance perspective, this creates a challenge:

* Controls don’t just live inside a single container.
* They often emerge from **platform abstractions** like service meshes, persistent volumes, or network policies.
* Compliance requires understanding both the **individual workloads** and the **shared infrastructure** that ties them together.

MapOSCAL’s new analysis routines help bring that structure into focus.

## Workload Groupings: Our Approach

When we looked at Kubernetes, we saw three natural groupings that repeat across deployments:

1. **Core Application Services** – The pods, containers, and deployments that implement business logic.
2. **Support Services** – Databases, caches, or message queues that provide application state or coordination.
3. **Platform Services** – Shared layers like ingress controllers, service mesh, and storage classes that handle transport, security, or resilience.

Instead of treating everything as flat, MapOSCAL groups resources into these categories. This lets us describe compliance responsibilities at the right level of abstraction.

For example:

* **Istio or Linkerd** can be the component that satisfies mTLS-related SC controls.
* A **Postgres StatefulSet** is its own component with AU or SC family controls.
* The **application Deployment** inherits certain platform guarantees while remaining accountable for its own logic-level controls.

## How This Manifests in OSCAL

The output of this grouping strategy is visible in the **OSCAL component definitions** MapOSCAL generates. Each grouping maps into one or more `component` entries with clear boundaries:

* **Application Components** list Dockerfile facts and workload-specific controls.
* **Infrastructure Components** like the ingress controller show how they enforce encryption or authentication at the edge.
* **Shared Capabilities** (e.g., service mesh mTLS) appear as implementation statements that can be referenced across multiple components.

This layered representation is powerful:

* It avoids duplication while keeping accountability clear.
* It makes it easier to trace “who satisfies what” when auditors or assessors look at a system.
* It sets the stage for combining Kubernetes analysis with cloud infrastructure analysis in future versions of MapOSCAL.

## Where We’re Headed

The Kubernetes analysis in v0.5.0 is just the start. Upcoming work will:

* Incorporate **network policies** and **RBAC roles** as compliance-relevant artifacts.
* Add options for **selective execution**, so users can choose which repositories or workloads to analyze when building a full OSCAL definition.
* Explore integration with **threat modeling frameworks** to extend compliance evidence into risk reasoning.

---

**Try it out:**
Grab the [v0.5.0 release](https://github.com/ChrisRimondi/MapOSCAL/releases/tag/v0.5.0), point MapOSCAL at a Kubernetes workload, and see how it groups components into OSCAL.

This release represents a big step toward making **compliance evidence as code** not only possible, but practical, in Kubernetes environments.



---

*Authored by [Chris Rimondi](https://www.linkedin.com/in/crimondi/)*
