# TakeMeter

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, the
> notebook, the baseline, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> head -5 data/practice_labels.csv     # the shape your labels.csv needs
> ```
>
> Then open `takemeter.ipynb` **in this folder** — in VS Code, or with
> `jupyter notebook` if you prefer. Pick the kernel: the `.venv` inside this
> project. Run section 1, which reports the hardware you'll be training on.
> Everything else waits until you have data.
>
> Nothing to upload, nothing to connect, no accounts and no keys. The notebook
> runs on your machine and writes next to your code.
>
> **The rest of this file is your submission.** Fill it in as you go.

## Stretch Features

**Stretch 1 (declared before starting): a fourth label, `news`.** r/wallstreetbets posts a lot of outside events (earnings, tariffs, lawsuits, headlines). The three core labels (`opinion`, `analysis`, `result`) have no place for a post whose main job is relaying that event, so `news` covers it.

**Stretch 2 (declared before starting): a second training run with one hyperparameter changed**, with a note on what moved. I will name the hyperparameter in the run log once I have the first run's results.

**Stretch 2 result.** I changed one thing: `EPOCHS` from 3 to 10. The seed (42), learning rate, batch size, token limit and split stayed the same. I picked epochs before the run because the first run's validation loss barely moved (1.34 to 1.28, against about 1.39 for a random guess), and three epochs is only about 27 gradient steps on 144 training posts. The second run is saved as `results_stretch2_epochs10.json`; `results.json` and `test_split.csv` still hold the first run.

| Measure on the same 32 test posts | Run 1 (3 epochs) | Run 2 (10 epochs) |
|---|---|---|
| Accuracy | 0.438 | 0.750 |
| Macro F1 | 0.344 | 0.707 |
| F1 `opinion` | 0.000 | 0.200 |
| F1 `analysis` | 0.250 | 0.857 |
| F1 `result` | 0.526 | 0.769 |
| F1 `news` | 0.600 | 1.000 |
| Accuracy, most confident third | 0.80 | 0.90 |
| Accuracy, least confident third | 0.30 | 0.60 |

What moved: `analysis` and `news` went from mostly wrong to mostly right, and the model got more careful about its own confidence. What did not move is `opinion`. Run 1 sent all 8 test `opinion` posts to `result`; run 2 sends 6 of 8 there and gets one right. More training taught the model the difference between an argument and an outside event, but not the line between a take and a personal outcome. It also over-calls `result`: recall 1.0, precision 0.62. This is one seed on 32 posts, so one post is about 3 points of accuracy, and `analysis` and `news` have only 7 test posts each. I read it as a direction, not a measurement, and I did not tune anything further after seeing it.

**Stretch 3: not pursued.** I declared it early, then dropped it because collecting 50 extra `analysis` posts was taking too much time. By then `analysis` was no longer my thinnest label (about 23% of the file).

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     Unit 5 asks for the first five sections. Unit 6 adds the five below them.

     Everything is pasted as TEXT. No screenshots, no images.

     ⚠️ The confusion matrix especially. The notebook prints one as a markdown
     table, ready to copy. A screenshot of a matrix earns nothing. Paste the
     table.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 5 — THE BUILD ═══════════════════════ -->

## What This Does

TakeMeter sorts posts from r/wallstreetbets, a public investing forum on Reddit, by what the post is doing. There are four labels: `opinion` (a mood, joke or view with nothing checkable behind it), `analysis` (a view backed by a number, catalyst or mechanism), `result` (the poster's own outcome or position) and `news` (an outside event or data). I picked this forum because quality varies so much: a one-line joke, a screenshot of a loss and a long thesis all sit in the same feed. The classifier reads only the text of a post, never the image, so I dropped posts whose meaning lived in a picture.

---

## Label Taxonomy

### `opinion`

**Definition:** The poster states a mood, joke or view, bullish or bearish, with no checkable support behind it.

**Example 1:**
> WE ARE SO FUCKING BACK

**Example 2:**
> The whole world has become a casino

### `analysis`

**Definition:** The poster argues a view or a trade using support a reader could check, such as a number, a catalyst or a causal mechanism.

**Example 1:**
> Anthropic are not going to be profitable. In 2025, Anthropic made $4b rev, -$46b costs for a net loss of -$42 billion.

**Example 2:**
> broad market is breaking down while top 10 big tech holds up the s&p 500 illusion. literally 66% of s&p 500 stocks are quietly bleeding out and hitting 52-week lows

### `result`

**Definition:** The poster states what they did, hold or got: an outcome (a gain, loss or "I'm up/down") or a bare position with no reason attached.

**Example 1:**
> 69 bagger, $30k -> $2.09mil. what a ride it's been holding on to these leaps for just over 2years. finally exercised.

**Example 2:**
> Good bye Wallstreet. From $200,000 to nearly $800,000 with some lucky call options, I think this is enough for me.

### `news`

**Definition:** The post relays facts or data about the market or the world, such as an event, a filing or compiled performance numbers, and not the poster's own outcome.

**Example 1:**
> President Trump says he will no longer be imposing 10% tariffs on EU countries on February 1st.

**Example 2:**
> Apple sues OpenAI alleging trade secret theft, says scheme was 'at every level'

### The hardest boundary

**Which two labels:** `result` and `analysis`

**The decision rule I used every time:**
If the post states the poster's own outcome on the position the post is about, it is `result`, even when most of the text is a thesis. If it argues for a position and states no outcome on it, it is `analysis`. A bare position with no reason is `result`. A past outcome on a different trade does not move a thesis post into `result`. The test is what the words say, not what they imply: "down 18%" with no owner is the market's move, not the poster's. The other boundary I hit often is `opinion` versus `analysis`. There, support has to be specific and checkable, so a joke, or a post that only challenges other traders, is `opinion` even when it names numbers or mechanisms.

---

## The Dataset

**Where the posts came from:** r/wallstreetbets, which is public and needs no login. I saved Reddit's public JSON listings from my browser (hot, new, and top of the week, month and year) plus searches for the DD and Discussion flairs. That gave 556 unique posts. I kept 207 and dropped any post whose label I could not tell from the title and body alone, mostly image and video posts, plus `[removed]` and empty threads.

**How I labeled them:** Rows come from three methods, and the `note` column in `labels.csv` names each one. `cold` (20 rows): I judged 30 posts against my written definitions with no tools, kept 20 and dropped 10 under the text-only rule. `discussed with Aurora` (43 rows): I labeled these in conversation with Claude, the assistant I called Aurora, while the definitions were still forming, so they are not cold. `pre-labeled, checked` or `pre-labeled, corrected` (144 rows): Claude proposed labels in five batches from my written definitions and rules, and I read and corrected every row (details under How I Used AI). Partway through I renamed `report` to `result`, because the old name kept pulling me toward "someone reports something" when the label means the poster's own outcome. The rename and the rule changes are logged in `notes.md`.

**Counts per label:**

| Label | Count | Share |
|---|---|---|
| `result` | 67 | 32% |
| `opinion` | 49 | 24% |
| `analysis` | 46 | 22% |
| `news` | 45 | 22% |
| **Total** | 207 | 100% |

**Three hard cases**

**1.**
> *The post:* "I am financially ruined (short selling Korean fried chicken companies)." It lays out a full thesis about Korea's declining population and healthier eating, then says "This week I lost $472,085."
>
> *Could have been:* `analysis` or `result`
>
> *I chose `result`, because* it states a specific dollar loss on the position the post is about, and a stated outcome beats a thesis in the same post.

**2.**
> *The post:* "THE DEFLATION GLITCH: Why $2 Bills are the ultimate hedge against the Fed." It cites circulation counts for $2 and $1 bills.
>
> *Could have been:* `analysis` or `opinion`
>
> *I chose `opinion`, because* it is satire. The numbers look like support, but the joke is the point, so a reader is not meant to dispute them.

**3.**
> *The post:* "Mean reversion traders - why are you so certain on bonds?" It names deficits, heavy treasury issuance and a higher term premium.
>
> *Could have been:* `analysis` or `opinion`
>
> *I chose `opinion`, because* it names mechanisms but only to challenge other traders. It makes no argument of its own that a reader could check.

---

## The Training Run

**Base model:** `distilbert-base-uncased`

**Settings:** 3 epochs, learning rate 2e-5, batch size 16, 128 tokens per post, seed 42. I trained on the CPU.

**Anything I changed from the defaults, and why:** Nothing. I kept the defaults so the first run is a clean reference point.

**Split sizes:** 144 train, 31 validation, 32 test. Test per label: `opinion` 8, `analysis` 7, `result` 10, `news` 7. `analysis` and `news` have fewer than 8 test examples, so their scores will swing between seeds. The notebook made the split at random within each label, so all three labeling methods appear in all three splits; the test split has 24 pre-labeled rows, 7 discussed and 1 cold.

---

## How I Used AI

**Moment 1**

- *What I asked for:* Claude wrote eight posts that sit on the boundaries of my four labels, and I labeled them blind from my definitions.
- *What came back:* On my first pass I matched its key on 4 of 8. The misses showed three gaps: "mechanism" had no definition, two near-identical posts (a position plus a reason) got different labels from me, and a news post with an opinion tail went the wrong way.
- *What I changed:* I added three written rules. Support has to be specific and checkable, a stated personal result decides `result` over `analysis`, and an outside event with an unsupported tail stays `news`. After those rules, one post still fit two labels because of how Claude had worded it, so I dropped it from the key.

**Moment 2**

- *What I asked for:* I asked Claude to draft five acceptance criteria, each with a number and a reason for it, and I accepted the drafts. Before filing them I asked a second AI model from a different vendor to review those five.
- *What came back:* It pointed out that an F1 target on only a handful of `analysis` test posts (about 4 at the time, 7 in the final split) is close to a coin flip, and that a confidence target built on thirds of about 10 posts is too noisy.
- *What I changed:* I replaced the `analysis` F1 target with a macro F1 target and report `analysis` F1 beside it without a pass or fail. I rebuilt the confidence criterion around mean confidence when right versus wrong, plus accuracy on the most confident third of predictions. I kept the balance and agreement criteria, and I rejected its suggestion to measure agreement against the model, because the agreement check is me against the course's 30-post staff set, not the model.

**Pre-labeling disclosure:** Claude pre-labeled 177 posts in five batches (12 to 45 posts each) from my written definitions and decision rules, with a one-line reason for each. I read every row. I changed 7 labels, dropped 18 posts that Claude had labeled under the text-only rule, agreed with its 15 proposed drops, and kept the remaining labels as proposed. The 144 rows from these batches that survived are in `labels.csv`, marked `pre-labeled` in `note`. The other 63 rows are the 20 cold rows and the 43 I labeled in conversation with Claude. The label definitions and every boundary rule are mine, and several came from disagreeing with Claude's proposed labels.

<!-- ═══════════════════════ UNIT 6 — THE TEST ═══════════════════════

     Don't fill these in during unit 5.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Baseline vs. Trained

<!-- Both models on the same posts. `python baseline.py --trained results.json`
     prints this table for you. -->

| Measure | Baseline | Trained | Difference |
|---|---|---|---|
| Overall accuracy |  |  |  |
| Macro F1 |  |  |  |
| F1 — `label_one` |  |  |  |
| F1 — `label_two` |  |  |  |

**What I predicted before I looked:**
<!-- Milestone 1 asks you to write this BEFORE seeing the trained numbers. A
     prediction made afterwards isn't one. -->

**What the gap actually means:**
<!-- If the baseline matched your trained model, your fine-tuning added
     nothing — and that is a real finding, not a failure. Say it plainly. -->



---

## Run Log — Before

<!-- Five criteria across three seeds. The notebook's section 6 prints the
     spread table; the Target and Verdict columns are yours. -->

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

### Confusion matrix

<!-- ⚠️ TYPED AS A MARKDOWN TABLE. The notebook prints one ready to paste.
     An image of a matrix earns nothing. -->

| true \ predicted |  |  |  |
|---|---|---|---|
| **** |  |  |  |
| **** |  |  |  |
| **** |  |  |  |

**My biggest off-diagonal number, and what it means:**
<!-- Not "the model made mistakes" — WHICH boundary it didn't learn, and which
     direction. "7 real analysis posts were called hot_take and only 3 went the
     other way" is a direction, not just an error rate. -->



---

## Verdicts and Diagnoses

<!-- MET or MISSED against LAST UNIT's target. The target has to hold across
     all three seeds, not turn up sometimes. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**

<!-- For each miss: the cause, and how you know. The four common causes are:
     too few examples for a label, a boundary you applied inconsistently, a
     genuinely hard label pair, and a task the model can't reach from this
     much data.

     ⚠️ Use your agreement report as evidence. It is the only instrument you
     have that can tell a LABELLING problem from a MODEL problem, and this
     section is graded on whether you used it that way. -->



---

## Agreement Report

<!-- Your rate against the staff set, and every disagreement adjudicated.

     Remember you labelled these 30 under the STAFF taxonomy in
     data/staff_taxonomy.md, not your own — so every argument below is made
     from those definitions and those decision rules. -->

**Agreement rate:** ___ / 30 = ___%

<!-- Nobody grades this number. A 60% who argues every disagreement from the
     stated rules beats a 95% who wrote "staff was right" nine times. Several
     of the 30 were chosen because they're genuinely ambiguous — you should be
     winning some of these. -->

**Disagreements**

<!-- Three lines each: the post, both labels, and who you think is right and
     why — grounded in the staff definitions you were both applying.

     Then sort each into one of three piles:
       (a) the rule covered it and I applied it loosely → a consistency problem
       (b) the rule genuinely doesn't say               → a gap in the definitions
       (c) the rule is ambiguous here and my reading is defensible → argue it.
           This is a legitimate win.

     Pile (a) is the one that matters most for your diagnosis: if you applied a
     written rule two different ways on 30 posts, that is direct evidence about
     what you did across your own 200. -->

**1.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**2.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**What the pattern in my disagreements tells me:**



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Run Log — After

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it didn't, say so. Relabelling that didn't help is a genuinely
     interesting result and earns full credit. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped. -->



**The gap between what I meant my labels to capture and what the model
learned:**
<!-- Two sentences. Your confusion matrix is the evidence. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 5

       [ ] criteria.md has five numbered criteria, each naming a NUMBER
       [ ] Each has a reason underneath tied to your data or taxonomy
       [ ] labels.csv: at least 150 rows, text/label/note, ONE file not split
       [ ] No label above 70%
       [ ] All five unit 5 sections have real content
       [ ] Label Taxonomy includes the decision rule for your hardest boundary
       [ ] The Dataset includes three hard cases
       [ ] results.json and test_split.csv committed (the notebook does this)
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 6

       [ ] Baseline vs. Trained table, with your prediction written beforehand
       [ ] Run Log — Before, five criteria across three seeds
       [ ] Confusion matrix TYPED AS A MARKDOWN TABLE
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, using the agreement report as evidence
       [ ] Agreement Report with every disagreement adjudicated
       [ ] One improvement, with Run Log — After
       [ ] What's Still Broken
       [ ] results_three_seeds_before.json, results_three_seeds_after.json,
           baseline_results.json and
           agreement_results.json committed
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
