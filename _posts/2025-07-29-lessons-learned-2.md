---
layout: post
title: "How We Used AI in MapOSCAL (Part 2 of 2)"
date: 2025-07-29 10:00:00 -0600
description: "Lessons learned using AI in building MapOSCAL."
tags: [AI, LLM, OSCAL, Open Source, Compliance, GitHub, Cybersecurity, JSON, DevTools, automation, Cursor, vibecoding]
categories: updates
---

# **How We Used AI to Help Build MapOSCAL (Part 2 of 2)**

This post is part two of a two-part series. In [part one](https://compliance.engineering/updates/2025/07/21/lessons-learned-1.html), we explored how we incorporated AI—specifically large language models (LLMs)—into the **design** of MapOSCAL. In this post, we’ll walk through how we used AI to help actually **build** the MapOSCAL tool itself.


### **Why We Built MapOSCAL**

[MapOSCAL](https://github.com/ChrisRimondi/MapOSCAL) is a tool designed to simplify the generation of OSCAL component definitions from real-world codebases. For those working in compliance automation, this typically involves mapping security controls (like those in NIST SP 800-53) to concrete evidence in software systems—often buried in code, configuration files, or documentation.


### **What Tools We Used to Build MapOSCAL**

- **Primary Models**: ChatGPT 4o and o3 for brainstorming and code prototyping  
- **Development Environment**: Cursor IDE  
- **Also Tried**: Visual Studio Code with GitHub Copilot, which was ultimately less effective than Cursor  

### **Brainstorming, Proof-of-Concepts, and Prompt Engineering**

For ideation, planning, and quick proof-of-concept code, we relied heavily on OpenAI’s 4o and o3 models. With the $20/month OpenAI subscription, we had UI access to both.

We used `o3` for open-ended exploration—often starting with questions that had no clear right answer. For example:

> “Think of ways SRGs, NAIP Common Criteria, and the NIST 800 control families express different groupings of controls. What are the similarities and differences? What can I learn from these observations to help build features for MapOSCAL?”

Because the OpenAI chat UI maintains long-running context, our working thread already included context about MapOSCAL, which helped responses stay grounded.

After a few back-and-forths, we would typically switch to `4o`—which was cheaper and faster—for generating specific examples or Python PoC code. Once we narrowed in on a use case, we’d iterate on what a good prompt would look like and fine-tune that prompt for integration into MapOSCAL’s logic.


### **Development Workflow**

As mentioned above, we ultimately settled on **Cursor** as our IDE after some experimentation. We initially tried VS Code with GitHub Copilot, but Cursor simply offered better responsiveness and higher quality suggestions.

That said, Cursor wasn’t perfect out of the box. Early on, it either didn’t do enough or did *too much*—often destructively. For example, when asked to update the parameters of a function, it might update the definition and just *some* of the instantiations. Other times, it made so many sweeping changes that we had to revert to a previous commit.

We’ll be the first to admit this was often a result of unclear or overly broad prompts. But even when scoped appropriately, the model would sometimes spiral into changes that weren’t recoverable. Fortunately, those issues seem to have disappeared in the last month or two, and the experience is now dramatically better.

We also noticed that early versions of Cursor had trouble with “logic loops”—repeating the same implementation ideas even after we had clearly stated they didn’t work. Today, Cursor seems to maintain context in a much more useful way. When we ask it to build a capability, it often automatically adds unit tests and updates docstrings.


### **Lessons Learned**

There are already a million articles out there on "vibe coding." We’re not going to pretend we’re adding something groundbreaking to that conversation.

But what we *will* say is this: agentic coding + deep knowledge of your own codebase = a force multiplier. That’s where the productivity gains really kick in.

Over time, we learned to be very targeted in our requests. Asking Cursor to perform a focused change led to dramatically better results. Once the architecture was stable—our libraries chosen, directory structure solidified, and modular design locked in—adding new capabilities and fixing bugs became much smoother.

For larger features or changes, we learned that asking Cursor to “think through the problem first” before writing code was incredibly helpful. We'd get a step-by-step implementation plan, which we could tweak before committing. We don’t know how Cursor routes those kinds of prompts internally, but it wouldn’t surprise us if it handled them differently—because the output quality was noticeably higher.


### **Conclusion**

This has been a great learning experience. We were consistently impressed by the evolution of Cursor—even over the span of just a few months. We also realized that **brainstorming outside the IDE** is often just as valuable as building inside it. Think of it like a whiteboard session with a team of expert engineers—before you even write a line of code.

---

*Authored by [Chris Rimondi](https://www.linkedin.com/in/crimondi/)*
