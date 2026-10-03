---
name: julie-homework
description: >
  Use this when making practice or homework pages for Julie Ansia (age 6,
  1st grade, Cherry Crest). Generate the questions with the grok CLI, draw
  a black-and-white CogAT-style PDF, and email it to Jerome and Ngoc.
---

# Julie’s homework

Standing playbook for practice PDFs for **Julie Ansia** (DOB 3 Dec 2019, age 6,
1st grade at Cherry Crest, BSD student ID 3027502). Cherry Crest school facts
live in `cherry-crest`. This skill is how to **make the pages**.

On a real ask: Titan retrieve, read this skill, then generate with the **grok
CLI** on this computer. After a change, update this file, append Titan, and
commit + push `jeromevidaao/localGrokSkills` (always-push). Never ask to push.

## Who gets the PDF

Email the finished PDF to **jerome.ans@gmail.com** and **ngoc.h.dinh@gmail.com**.
Jerome’s standing approval (2026-10-03) is to send the packet, not leave it as
a draft-only card. Subject: `Julie practice — <what it is> <date>`.

## How to generate

Grok writes the questions. A drawing script only lays them out. Do not invent
the item logic in the drawing script alone.

```bash
python3 /workspace/localGrokSkills/skills/r2-memory/scripts/r2_retrieve.py "Julie homework CogAT"
# write the full ask to a file, then:
grok --prompt-file /tmp/julie-homework-ask.txt --always-approve --output-format plain --max-turns 20 --verbatim
```

Use `--prompt-file` or `-p`, never both. Run `grok` on this computer only.

The prompt to grok must include every rule below. Ask it to return a page plan
(one format per page, the relation or pattern, and which choice is correct)
before any PDF is drawn. Reject a plan that uses the wrong item shape.

## Question format (Bellevue CogAT)

BSD grade 1 uses **CogAT Form 7 or 8, Level 8**. Picture items, audio-led on
the real test. Source: https://www.bsd405.org/academics/advanced-learning/tests
and the district sample PDF for Forms 7 and 8, Levels 5/6–8.

Friendly to a 6-year-old: large outline pictures, one short instruction line,
almost no reading. One format per page. Several items so the page is not empty.
Original drawings only. Do not copy Riverside sample art.

BSD does **not** use Sentence Completion for grades K–2. No word analogies,
no heart-word grids, no sound-it-out rows, no copy-the-sentence lines, no
addition worksheets. Jerome rejected that worksheet style on 2026-10-03.

| Format | What the child sees |
|---|---|
| Picture Analogies | One pair of pictures that go together, then **option pairs**. Choose the pair that goes together the same way. The answer is a pair, not a single picture in a dashed box. |
| Picture Classification | Three pictures that are alike, then choose the picture that belongs in that group. |
| Number Analogies | A 2×2 grid of amounts. Bottom-right is missing. |
| Number Puzzles | Two trains. Choose what makes the second train carry the same number as the first. |
| Number Series | Bead strings in a pattern. Choose the string that comes next. |
| Figure Matrices | A 2×2 grid of shapes. Bottom-right is missing. |
| Paper Folding | Paper folded once and punched. Choose what it looks like opened. |
| Figure Classification | Three shapes that are alike, then choose the one that belongs. |

Pictures may use objects from that week’s Classroom Newsletter, but the
question shape stays CogAT.

## Page rules

- About 10 letter pages unless Jerome asks for a different length.
- **No name line. No date line.**
- Black and white only. No color, no gray fills, no large solid black areas.
  Outline drawings, thin lines.
- Each new packet is better than the last: reuse a few earlier relations in a
  slightly harder form, and fold in learning gaps recorded in `cherry-crest`.

## After sending

Record the date and what each page practiced in `cherry-crest` (packet log).
Tell Jerome the PDF went out, with the page count and both recipients.
Quiet-on-empty for the school-mail scan does not cover a packet that was sent.
