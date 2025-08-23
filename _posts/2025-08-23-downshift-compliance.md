---
layout: post
title: "Downshifting Compliance"
date: 2025-08-23 10:00:00 -0600
description: "Embedding Compliance into Platform Abstractions"
tags: [Platform Engineering, OSCAL, Open Source, Compliance, Cybersecurity, JSON, DevTools, automation, DevOps, SRE, SSP]
categories: updates
---

## **Downshifting Compliance**

### **Introduction**: Embedding Compliance into Platform Abstractions**

Engineering teams constantly balance efficiency, quality, and cost, all while delivering value to customers. Compliance is often treated as something bolted on at the end of the process, creating overhead and slowing teams down.

But there’s a better way. In a recent talk from Google at PlatformCon 2025, they emphasized the idea of **“shift down”**: 

> Shift down is an approach that advocates for embedding decisions and responsibilities into underlying internal developer platforms (IDPs), thereby reducing the operational burden on developers. This contrasts with the DevOps trend of "shift left," which pushes more effort earlier into the development cycle, a method that is proving difficult at scale due to the sheer volume and rate of change in requirements.

We think this type of thinking applies equally in the compliance space.



### **The Compliance Leverage of Platforms**

When we analyzed a System Security Plan (SSP), one insight stood out: **not all components are equal when it comes to compliance leverage.**

Some parts of the stack contribute far more to compliance than others. For example:

* A Kubernetes **Ingress Controller** that enforces TLS and mTLS delivers massive compliance leverage.
* A service mesh that ensures **zero-trust networking** applies to every workload without extra developer effort.
* A hardened base image contributes compliance to all workloads built on top of it.

Contrast that with individual app teams rolling their own TLS logic. It’s inefficient, inconsistent, and hard to audit.



### **OSCAL as a Modeling Tool**

This is where OSCAL comes in. Within the OSCAL Component Definition model:

* **Components** represent discrete systems or services (e.g., “Kubernetes Ingress Controller”).
* **Capabilities** are reusable compliance functions that span multiple components (e.g., “Terminate ingress TLS with mTLS to backends”).

By modeling both, OSCAL gives you a map of **where compliance actually lives in your stack.**



### **Shifting Down with Capabilities**

Capabilities can hold the *primary* implementation of cross-cutting controls. Workloads can then reference—or inherit—these implementations instead of duplicating them.

* Example:

  * Capability: “All ingress TLS is terminated by the Ingress Controller with mTLS to backends.”
  * Workloads: Simply depend on this capability; they don’t need their own custom TLS implementation.

This reduces duplication, ensures consistency, and makes audits simpler.



### **Case Study: Compliance Inheritance**

Imagine a simple stack:

* **Platform layer**: Istio Service Mesh implements mTLS for all services.
* **Workload layer**: Applications only need to integrate with the mesh.

In OSCAL:

* The platform component definition describes the mTLS capability.
* Application component definitions reference that capability.

Compliance evidence is tied to the platform once—not re-documented for every workload.



### Example OSCAL YAML Snippet**

Here’s how the above example might be represented in OSCAL YAML:


```
component-definition:
  uuid: "22222222-2222-4222-8222-222222222222"
  metadata:
    title: "Shift Down: Platform-Delivered Compliance Primitives"
    last-modified: "2025-08-23T12:00:00Z"
    version: "1.0.0"
    oscal-version: "1.1.3"
    parties:
      - uuid: "aaaaaaa1-0000-4000-8000-aaaaaaaaaaa1"
        type: organization
        name: "Platform Team"
  components:
    # --- Workload that inherits TLS/mTLS from the platform capability ---
    - uuid: "33333333-3333-4333-8333-333333333333"
      type: "software"
      title: "orders-api"
      description: >
        A workload service that relies on platform-provided ingress TLS termination and
        mesh-provided mTLS to backends. It does not roll its own TLS.
      control-implementations:
        - uuid: "44444444-4444-4444-8444-444444444444"
          source: "https://doi.org/10.6028/NIST.SP.800-53r5"   # NIST 800-53 Rev 5
          description: "Workload inherits network protection from platform capability."
          implemented-requirements:
            # SC-8: Transmission Confidentiality and Integrity
            - uuid: "55555555-5555-4555-8555-555555555555"
              control-id: "sc-8"
              props:
                - name: "implementation-status"
                  value: "inherited"
                - name: "inherited-from"
                  ns: "https://example.com/oscal/relations"
                  value: "capability:11111111-1111-4111-8111-111111111111"
              statements:
                - statement-id: "sc-8_smt"
                  description: >
                    All external ingress traffic is terminated via platform ingress with TLS 1.2+
                    and traffic to backends is mTLS-encrypted via the service mesh.
            # SC-13: Cryptographic Protection
            - uuid: "66666666-6666-4666-8666-666666666666"
              control-id: "sc-13"
              props:
                - name: "implementation-status"
                  value: "inherited"
                - name: "inherited-from"
                  ns: "https://example.com/oscal/relations"
                  value: "capability:11111111-1111-4111-8111-111111111111"
              statements:
                - statement-id: "sc-13_smt"
                  description: >
                    Workload uses FIPS-validated crypto libraries as enforced by platform ingress
                    and mesh policy; no local crypto is implemented in the service.

  # --- Platform capability holds the primary implementation for cross-cutting controls ---
  capabilities:
    - uuid: "11111111-1111-4111-8111-111111111111"
      title: "Ingress TLS termination with mTLS to backends"
      description: >
        Platform-delivered network protection: TLS 1.2+ termination at ingress, certificate
        management, and mutual TLS for service-to-service communication via the mesh.
      props:
        - name: "provided-by-component"
          ns: "https://example.com/oscal/relations"
          value: "component:77777777-7777-4777-8777-777777777777"   # links to the platform component below
      control-implementations:
        - uuid: "99999999-9999-4999-8999-999999999999"
          source: "https://doi.org/10.6028/NIST.SP.800-53r5"
          implemented-requirements:
            - uuid: "aaaa1111-aaaa-4111-8111-aaaaaaaaaaa1"
              control-id: "sc-8"
              statements:
                - statement-id: "sc-8_smt"
                  description: >
                    Enforce TLS 1.2+ at ingress, HSTS, strong ciphers; forward traffic to
                    backends using authenticated mTLS between sidecars.
              responsible-roles:
                - role-id: "platform-ops"
            - uuid: "bbbb2222-bbbb-4222-8222-bbbbbbbbbbb2"
              control-id: "sc-13"
              statements:
                - statement-id: "sc-13_smt"
                  description: >
                    Use FIPS 140-3 validated modules for TLS termination and mesh mutual auth;
                    keys and certs managed by platform PKI/CMC workflows.
              responsible-roles:
                - role-id: "platform-ops"

  # --- Concrete platform component that provides the capability above ---
  components:
    - uuid: "77777777-7777-4777-8777-777777777777"
      type: "software"
      title: "platform-networking"
      description: >
        Kubernetes Ingress Controller + Service Mesh (e.g., Istio) delivering TLS termination,
        mTLS, and policy enforcement across all workloads.
      props:
        - name: "capability-provided"
          ns: "https://example.com/oscal/relations"
          value: "capability:11111111-1111-4111-8111-111111111111"
```


### **Why This Matters**

For engineering teams:

* Reduced toil and duplicate work.
* Compliance becomes part of the developer experience.
* Faster delivery without sacrificing quality.

For compliance teams:

* Clear responsibility boundaries in SSPs.
* Easier evidence collection and audits.
* Stronger posture by enforcing controls at the right layer.


### **Conclusion**

Shifting compliance down into platforms is more than a compliance strategy — it’s an engineering acceleration strategy.

The question to ask: *Where in your stack should compliance primitives live?*

By using OSCAL to model components and capabilities, teams can visualize these leverage points, reduce wasted effort, and deliver both faster and safer.


---

*Authored by [Chris Rimondi](https://www.linkedin.com/in/crimondi/)*
