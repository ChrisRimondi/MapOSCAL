---
layout: post
title: "How We Used AI in MapOSCAL (Part 1 of 2\)"
description: "Lessons learned integrating AI into a compliance automation tool for generating OSCAL component definitions."
date: 2025-07-21
tags: [AI, LLM, OSCAL, Open Source, Compliance, GitHub, Cybersecurity, JSON, DevTools, automation]
categories: updates
---

# **How We Used AI in MapOSCAL (Part 1 of 2\)**

This post is part one of a two-part series. In this first installment, we’ll explore how we incorporated AI—specifically large language models (LLMs)—into the design of MapOSCAL. In part two, we’ll walk through how we used AI to help us *build* the MapOSCAL tool itself.

## **Why We Built MapOSCAL**

[MapOSCAL](https://github.com/ChrisRimondi/MapOSCAL) is a tool designed to simplify the generation of OSCAL component definitions from real-world codebases. For those working in compliance automation, this typically involves mapping security controls (like those in NIST SP 800-53) to concrete evidence in software systems—often buried in code, configuration files, or documentation.

Our goal was to make that mapping process faster and more accurate by applying AI to automate portions of the analysis. Along the way, we learned a lot—especially about what *not* to do with LLMs.

---

## **How We Use AI in the Tool**

### **Why We Didn’t Use Agentic AI**

From the beginning, we chose not to use agentic AI frameworks (like LangChain or crewai). While appealing in theory, these systems introduce significant complexity—particularly in managing state, chaining actions, and recovering from failure that our use case simply didn’t warrant. 

Instead, we adopted what we jokingly refer to as “agentic-lite.” Our approach breaks the problem into discrete tasks and selectively uses LLMs when they add real value, while retaining full control of the overall workflow in traditional Python code. This struck a balance between automation and reliability.

---

## **Phantom Configurations: When AI Hallucinates Settings**

One early pitfall we hit was asking the LLM to identify configuration values relevant to specific controls. For instance, if a control required TLS, we’d prompt the model to extract or infer relevant config like:

"file": "/etc/service.conf",  
"enable\_tls": "true"

The problem? Many times these values were entirely hallucinated—convincing, plausible, but totally made up.

To fix this, we shifted strategies. Rather than asking the model to invent configuration values, we manually parsed the project directory to find files with known configuration extensions (like `.conf`, `.yaml`, etc.) and patterns (e.g., use of `os.getenv`, `configparser`, or `dotenv`). Then, we limited the model’s context and responses strictly to the actual values found.

Lesson learned: if a configuration doesn’t exist in the repo, don’t let the model make it up.

---

## **The Structured Output Struggle: Why (too much) JSON is a Poor Fit for LLMs**

In early versions of MapOSCAL, we gave the LLM a sample of the OSCAL JSON structure and asked it to produce structured output directly.

This went poorly.

We often got malformed JSON or values that looked right but failed schema validation. So we tried a fallback: send the broken output back to the LLM and ask it to fix the formatting.

That also didn’t work well. The LLM would sometimes fix issues, but more often it didn’t—or it would break something else in the process. It also slowed the tool down and increased API costs.

Eventually, we learned to stop fighting the model. Instead, we asked it only for the parts we truly needed—descriptions, summaries, implementation text. We handled all structure and validation in our code. LLMs are powerful language tools, not database serializers.

---

## **Where AI Shined: The Feedback Flywheel**

While some tasks were a poor fit for LLMs, others turned out to be ideal.

One example: evaluation. We took the implementation statements the model produced and asked it to grade them on clarity, completeness, and accuracy using a 1–4 numeric scale, plus a short rationale.

With enough samples, we could feed those back into the LLM to identify patterns. We even asked it to suggest product improvements and identify common pitfalls. The model essentially helped us review itself.

Another key enhancement: we made the model configurable per task. We could run cheap models like `gpt-4o-mini` for quick summaries, and reserve premium models like `gpt-4o` for more nuanced mappings. We also allowed for multiple providers (OpenAI, Gemini, etc.) to simulate dual-control evaluations.

---

## **Conclusion: Two Key Takeaways**

We’re still early in this journey, but two key lessons stand out:

1. **Context is everything.** We learned to think less like prompt engineers and more like *context engineers*. Getting the right context into the model—at the right time—is the difference between brilliance and nonsense.  
2. **LLMs \+ Traditional Code \- Greater than the sum of their parts.** Combining LLMs with traditional parsing, validation, and deterministic logic is far more effective than either on its own. When used together, they unlock workflows that would be impossible—or prohibitively expensive—otherwise.

Authored by: [Chris Rimondi](https://www.linkedin.com/in/crimondi/)