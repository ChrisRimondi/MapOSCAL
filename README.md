# MapOSCAL

## TL;DR
Software muust be accurately described for security and compliance purposes.  NIST's OSCAL appears to be the defined format of the immediate future, but usability isn't ready for widespread, industry usage.  This project makes OSCAL usable by providing automated discovery in an engineering-friendly CLI tool, which enables your security architects to be focused on the details, not the documentation generation!

## Overview

Cybersecurity, risk management, as well as regulatory compliance requirements all hinge on a method to accurately describe your system's working environment and configuration.  The purpose of this project is to assist the software industry in easily creating standardized software component definitions, specifically to further the interoperability of security and compliance requirements.  This takes place using a foundation of the [Open Security Controls Assessment Language (OSCAL)](https://pages.nist.gov/OSCAL/) framework developed by the National Institute of Standards and Technology (NIST).  Creation of the OSCAL-based service definition is handled using the Cloud Native Computing Foundation's [Compliance Trestle (a.k.a. Trestle)](https://github.com/oscal-compass/compliance-trestle) project.

Creating and maintaining an OSCAL definition of your software is not a trivial task.  With OSCAL being a machine-readable format, it's usually accessed as JSON or XML, or using an SDK such as Trestle.  Some UI's exist to improve human interaction, however, it's still a tedious process that requires significant subject matter expertise for mundane tasks.  This project seeks to simplify that pain-point by providing an engineering-focus CLI (and GIT-enabled webhook) that, allows for the dynamic drafting of your OSCAL system defintion based on automated discovery techniques.  Released under the generous MIT License, it's goal is to provide core discovery functionality to as wide an audience as possible.  Using the generated output, your system's SMEs (with their highly-valued time) load is shifted from weeks of creating tedious documentation to a more effecient review process of automatically generated documentation.  It's goal and purpose is not to replace such individuals, but to enable them to serve where their expertise is most valuable, not drafting documentation.

### Generative AI and OSCAL Discovery

While extremely powerful, generative AI can be equally dangerous in producing false, hallucinatory results if not properly implemented with guardrails.  The benefits of using generative AI are only valuable when produced in a framework that allows its powerful pattern-recognition to be assured by non-generative methods.  In this open source project, pains have been taken to place guardrails at a high-level view of your application.  If there is project growth, in a future commercial version there is planned to be much more granular controls, moving from the application and file level, into functions, relationships, and other more granular aspects.

### Compliance Control Implementation Statements

Having an OSCAL-based system defintion is only half of the compliance battle.  To be truely effective that definition must be distilled into accurate implementation statements that are tied to one or more compliance frameworks.  In this open source implementation we have included a single control definition and mapping for example purposes.  If future growth occurs, more are desired to be offered as part of a future commercial offering.

### Future Growth

The industry is currently struggling to have a clean, clear, and actionable way to describe systems for security and compliance purposes.  The ideal path forward for this is two-fold:

1. **Open source adoption** -  Having a wide-spread use of OSCAL across both commercial/propriatary as well as commonly-used open source projects is key to future, normalized usage and adoption.  This movement grows everytime a project is defined in OSCAL and available for usage by others.

2. **Robust commercial support** - This project, while currently open-source, is desirable to  to have commercial add-ons in the future.

## Tool Usage

The tool is simple and straight-forward to use, either by individual engineers, or ideally as part of your CI/CD process via our Git hook.

< Examples HERE >









