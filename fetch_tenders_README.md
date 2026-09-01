# How to run the tender fetcher

File: fetch_tenders.py (in this same folder)

## Why you run this yourself (for now)
Claude's cloud workspace and its sandboxed shell on this computer are both
blocked from reaching government tender websites directly (network policy).
Your own computer, running this script in a normal Command Prompt/PowerShell
window (not through Claude), has full internet access, so it works there.

## One-time setup
1. Make sure Python is installed (check by running: python --version).
2. Open Command Prompt in this folder (02-Tender-Intelligence).
3. Run: pip install requests

## Run it
   python fetch_tenders.py

This creates two files in the same folder:
- tenders_digest.md — a readable list of matching IT/software tenders
- tenders_raw.json — the same data, structured, for later automation

## Current coverage
- UK Find a Tender: fully working (official free API).
- Australia AusTender: not wired up yet — needs the exact live API endpoint
  confirmed first.
- EU TED and US SAM.gov: not in this version yet (SAM.gov needs your API key
  from the registration steps we covered — send it over when you have it and
  I'll add it in).

## Automating it daily (optional, later)
Once this runs cleanly by hand a few times, two options to make it automatic:
1. Windows Task Scheduler — runs this script on your machine every day at a
   set time, no cloud hosting needed, zero cost.
2. A small always-on service on Railway (you already have a Railway account) —
   needs a GitHub repo connected to Railway so it can deploy the code; this
   is the path to a real-time paid-alert product later, but requires you to
   create/connect a GitHub repo first (a Claude session can help push the code
   once that's set up).

Send me the output (or just tell me it ran and how many results came back) and
I'll turn the results into the next digest content piece.
