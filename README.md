# MapOSCAL

## TL;DR
Software must be accurately described for security and compliance purposes.  NIST's OSCAL appears to be the defined format of the immediate future, however industry adoption hasn't reached its potential.  This project makes OSCAL usable by providing automated discovery in an engineering-friendly CLI tool, which enables your security architects to be focused on the details, not the documentation generation!

## Overview

Cybersecurity, risk management, as well as regulatory compliance requirements all hinge on a method to accurately describe your system's working environment and configuration.  The purpose of this project is to assist the software industry in easily creating standardized software component definitions, specifically to further the interoperability of security and compliance requirements.  This takes place using the foundation of [Open Security Controls Assessment Language (OSCAL)](https://pages.nist.gov/OSCAL/) Framework developed by the National Institute of Standards and Technology (NIST).  

Creating and maintaining an OSCAL definition of your system/software is not a trivial task.  With OSCAL being a machine-readable format, it's usually accessed as JSON or XML, or using an programmatic SDK.  Some UI's exist to improve human interaction, however, it's still a tedious process that requires significant subject matter expertise for mundane tasks.  This project seeks to simplify that pain-point by providing an engineering-focused CLI interface that allows for the dynamic drafting of your OSCAL system defintion based on automated discovery techniques.  Released under the generous MIT License, its goal is to provide core discovery functionality to as wide an audience as possible.  Using the generated output, your system's SMEs (with their highly-valued time) load is shifted from weeks of creating tedious documentation to a more effecient review process of automatically-generated documentation.  Its goal and purpose is not to replace such individuals, but to enable them to serve where their expertise is most valuable, not drafting documentation.

### Generative AI and OSCAL Discovery

While extremely powerful, generative AI can be equally dangerous in producing false, hallucinatory results if not properly implemented with guardrails.  The benefits of using generative AI are only valuable when produced in a framework that allows its powerful pattern-recognition to be assured by non-generative methods.  In this open source project, pains have been taken to place guardrails at a high-level view of your application.  If there is project growth, in a future commercial version there is planned to be much more granular controls, moving from the application and file level, into functions, relationships, and other more granular aspects.

### Compliance Control Implementation Statements

Having an OSCAL-based system defintion is only half of the compliance battle.  To be truely effective that definition must be distilled into accurate implementation statements that are tied to one or more compliance frameworks.  In this open source implementation we have included a single control definition and mapping for example purposes.  If future growth occurs, more are desired to be offered as part of a future, commercial offering.

### Future Growth

The industry is currently struggling to have a clean, clear, and actionable way to describe systems for security and compliance purposes.  Our view is that the ideal path forward to improve this problem space is two-fold:

1. **Foundational open source adoption** -  Having a wide-spread use of OSCAL across both commercial/propriatary as well as commonly-used open source projects is key to future, normalized usage and adoption.  With such service definitions an accurate, building-block approach can be achieved to accurately describe complex systems.  This movement grows everytime a project is defined in OSCAL and available for usage by others.

2. **Robust commercial support** - While this project is foundational and released as open source, requires significant investment in ongoing compliance-related content generation and maintenance.  As such, it is desirable to have commercial add-ons in the future to benefit users with turn-key compliance needs.

## Tool Usage

The tool is simple and straight-forward to use for native CLI-based analysis of your software!

< Examples HERE >
