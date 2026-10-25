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

**Unit 6 Stretch A (declared before starting): a confidence check.** I will test whether the model's confident predictions are right more often than its unsure ones. For each of the three seeds I split the 32 test posts into thirds by confidence and compare accuracy across the thirds. This reuses criterion 5, and the table goes in Run Log — Before.

**Unit 6 Stretch B (declared before starting): a per-label error write-up** for whichever label the confusion matrix shows is worst. I expect `opinion`, because in my Stretch 2 run it lost 6 of 8 test posts to `result`, but the matrix decides.

**Unit 6 Stretch C (declared before starting): a second improvement**, measured the same way as the first: change one thing, retrain on the same three seeds, and put both result sets side by side. I will pick it after the first improvement's results are in. Labels, taxonomy and criteria stay where they were for both improvements.

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

Baseline: `facebook/bart-large-mnli`, zero-shot, with my four definitions from `label_definitions.txt`. Trained: the 3-epoch run in `results.json`. Both are scored on the same 32 posts in `test_split.csv`, so the comparison is like-for-like.

| Measure | Baseline | Trained | Difference |
|---|---|---|---|
| Overall accuracy | 0.188 | 0.438 | +0.250 |
| Macro F1 | 0.086 | 0.344 | +0.258 |
| F1 — `analysis` | 0.343 | 0.250 | -0.093 |
| F1 — `news` | 0.000 | 0.600 | +0.600 |
| F1 — `opinion` | 0.000 | 0.000 | +0.000 |
| F1 — `result` | 0.000 | 0.526 | +0.526 |

The same baseline with bare label names instead of my definitions (`baseline_results_bare_names.json`), which I ran once on purpose to measure what the definitions were worth:

| Measure | Baseline, bare names | Trained | Difference |
|---|---|---|---|
| Overall accuracy | 0.375 | 0.438 | +0.062 |
| Macro F1 | 0.303 | 0.344 | +0.042 |
| F1 — `analysis` | 0.000 | 0.250 | +0.250 |
| F1 — `news` | 0.286 | 0.600 | +0.314 |
| F1 — `opinion` | 0.444 | 0.000 | -0.444 |
| F1 — `result` | 0.480 | 0.526 | +0.046 |

**What I predicted before I looked:**
<!-- Milestone 1 asks you to write this BEFORE seeing the trained numbers. A
     prediction made afterwards isn't one. -->

I predict the trained model (the 3-epoch run in `results.json`) beats the baseline only on `result`, my largest label, and loses overall, because three epochs on 144 posts barely moved the validation loss while the baseline gets my full definitions. (Written before running `baseline.py`; I had already seen the trained numbers, so this is not blind on that side.)

**What the gap actually means:**
<!-- If the baseline matched your trained model, your fine-tuning added
     nothing — and that is a real finding, not a failure. Say it plainly. -->

My prediction was half right. The trained model did beat the baseline on `result` (0.526 against 0.000), but it also won on `news` and overall, so "only on `result`" and "loses overall" were both wrong.

The baseline with my definitions scored 0.188 accuracy, below the 0.25 that a random guess earns on four labels. Nearly all of it is one failure: it called 28 of 32 posts `analysis`. That took in all 7 `news` posts, 7 of 8 `opinion` posts and 8 of 10 `result` posts, and it is also why `analysis` has the baseline's best F1 (0.343): it got 6 of 7 right and mislabeled 22 others. My guess at the cause, which I did not test, is that `baseline.py` slots each definition into "This post is {}.", and my `analysis` definition is the one that reads like something a post can match, while `opinion` is defined mostly by what is missing.

With bare label names the baseline did better: 0.375 accuracy and 0.303 macro F1, spread over `result` (15 predictions), `opinion` (10) and `news` (7), and never `analysis`. So my definitions were worth about -19 points of accuracy to this model: they made it worse, not better. I am reporting the with-definitions run as the baseline because that is the run the milestone asks for, and the bare-names run is beside it.

Against the stronger bare-names baseline, the trained model's lead shrinks to 0.062 accuracy, and it loses `opinion` outright (0.000 against 0.444). Three epochs of fine-tuning added little over a zero-shot guess from label names. The test split is 32 posts, so one post is about 3 points and none of these gaps is precise.



---

## Run Log — Before

<!-- Five criteria across three seeds. The notebook's section 6 prints the
     spread table; the Target and Verdict columns are yours. -->

Fine-tuned `distilbert-base-uncased` on CPU (`device: cpu`, torch 2.14.1+cu130): 10 epochs (the setting I chose in Stretch 2), learning rate 2e-5, batch size 16, 128 tokens per post. Each seed gives a different 144 / 31 / 32 split of the same 207 posts. The per-label test counts are the same on every seed (7 `analysis`, 7 `news`, 8 `opinion`, 10 `result`). Numbers come from `results_three_seeds_before.json`.

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1. Accuracy | at least 0.60 on all three seeds | 0.750 | 0.625 | 0.719 | Met (seed 7 clears it by one post: 20 of 32, where 19 would have failed) |
| 2. Macro F1 and per-label F1 | on all three seeds, macro F1 at least 0.50 and F1 at least 0.50 for `opinion`, `news` and `result` | macro 0.707<br>`opinion` 0.200<br>`news` 1.000<br>`result` 0.769 | macro 0.585<br>`opinion` 0.222<br>`news` 0.857<br>`result` 0.762 | macro 0.648<br>`opinion` 0.222<br>`news` 0.750<br>`result` 0.870 | Missed on `opinion` only (0.20 to 0.22 on every seed); macro F1, `news` and `result` all passed |
| 3. Balance | no label above 50% or below 12% of `labels.csv` | 32% to 22% | same file | same file | Met. The mix moved after I wrote the criterion, which cites `opinion` at 42% of my first 43 rows; the final file is `result` 32%, `opinion` 24%, `analysis` 22%, `news` 22% |
| 4. Agreement with staff | at least 21 of 30 | 28 of 30 | same file | same file | Met (93%) |
| 5. Confidence | on all three seeds, mean confidence higher when right than wrong, and accuracy at least 0.60 in the most confident third | right 0.576, wrong 0.471<br>top third 0.90 | right 0.573, wrong 0.447<br>top third 0.90 | right 0.582, wrong 0.477<br>top third 0.90 | Met |

`analysis` F1, reported beside criterion 2 without a pass or fail: 0.857, 0.500, 0.750.

The full spread table from section 6:

| Measure | Seed 42 | Seed 7 | Seed 2024 | Spread |
|---|---|---|---|---|
| Overall accuracy | 0.750 | 0.625 | 0.719 | 0.125 |
| Macro F1 | 0.707 | 0.585 | 0.648 | 0.121 |
| F1 — `opinion` | 0.200 | 0.222 | 0.222 | 0.022 |
| F1 — `analysis` | 0.857 | 0.500 | 0.750 | 0.357 |
| F1 — `result` | 0.769 | 0.762 | 0.870 | 0.108 |
| F1 — `news` | 1.000 | 0.857 | 0.750 | 0.250 |

**The spread.** Accuracy moved 0.125 across the three seeds and macro F1 moved 0.121 (from the unrounded values, 0.7066 and 0.5853), both over the brief's ten-point threshold for a stable measure. The spread comes from the 32-post test split: one post is about 3 points of accuracy, so four posts are enough to cross the line. `analysis` (0.357) and `news` (0.250) swung most, and both have 7 true posts per split. On seed 7 `analysis` precision fell to 0.385 (5 of 13 `analysis` predictions were right), so on that split the model over-called `analysis`, and one post does not explain that. `opinion` is the opposite case: its F1 barely moved (0.022) because it stayed bad on every seed, so for that label the problem is not noise.

**Stretch A, the confidence check.** On all three seeds the confident predictions were right more often than the unsure ones:

| Seed | Accuracy, most confident third (10 posts) | Accuracy, least confident third (10 posts) | Mean confidence when right | Mean confidence when wrong |
|---|---|---|---|---|
| 42 | 0.90 | 0.60 | 0.576 | 0.471 |
| 7 | 0.90 | 0.40 | 0.573 | 0.447 |
| 2024 | 0.90 | 0.60 | 0.582 | 0.477 |

The most confident third was right 9 times in 10 on every seed. The gap between right and wrong is small in absolute terms (about 0.10 to 0.13 of confidence), and a third is only 10 posts, so a single post moves it 10 points. I read it as confidence pointing the right way on 10-post thirds: a direction, not a calibrated probability.

### Confusion matrix

<!-- ⚠️ TYPED AS A MARKDOWN TABLE. The notebook prints one ready to paste.
     An image of a matrix earns nothing. -->

Seed 42 (the one section 7 prints), rows are the true label and columns are the model's guess:

| true \ predicted | opinion | analysis | result | news |
|---|---|---|---|---|
| **opinion** | 1 | 1 | 6 | 0 |
| **analysis** | 1 | 6 | 0 | 0 |
| **result** | 0 | 0 | 10 | 0 |
| **news** | 0 | 0 | 0 | 7 |

**My biggest off-diagonal number, and what it means:**
<!-- Not "the model made mistakes" — WHICH boundary it didn't learn, and which
     direction. "7 real analysis posts were called hot_take and only 3 went the
     other way" is a direction, not just an error rate. -->

On seed 42, 6 real `opinion` posts were called `result` and 0 real `result` posts were called `opinion`. The model predicted `result` 16 times for 10 true `result` posts, and only 1 of the 8 `opinion` posts came back right (recall 0.125). That is the `opinion` to `result` boundary, with the errors running one way. The other two seeds show the same weak `opinion` (1 of 8 right each) but a different destination: on seed 7, 5 of the 8 went to `analysis` and 2 to `result`, and on seed 2024 they scattered across `result` (3), `analysis` (2) and `news` (2). So the `opinion` failure holds on every seed, while which label absorbs it changes with the split. `news` misses 0, 1 and 1 posts and `result` misses 0, 2 and 0. `analysis` misses 1, 2 and 1, so it is never fully clean either. The `opinion` to `result` direction is one-seed evidence, so I treat it as a lead for the diagnosis, not a finding, and I have not tested why.

Seed 7:

| true \ predicted | opinion | analysis | result | news |
|---|---|---|---|---|
| **opinion** | 1 | 5 | 2 | 0 |
| **analysis** | 0 | 5 | 1 | 1 |
| **result** | 0 | 2 | 8 | 0 |
| **news** | 0 | 1 | 0 | 6 |

Seed 2024:

| true \ predicted | opinion | analysis | result | news |
|---|---|---|---|---|
| **opinion** | 1 | 2 | 3 | 2 |
| **analysis** | 0 | 6 | 0 | 1 |
| **result** | 0 | 0 | 10 | 0 |
| **news** | 0 | 1 | 0 | 6 |

---

## Verdicts and Diagnoses

<!-- MET or MISSED against LAST UNIT's target. The target has to hold across
     all three seeds, not turn up sometimes. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Accuracy | at least 0.60 on all three seeds | MET | 0.750, 0.625, 0.719. Seed 7 clears it by one post (20 of 32). |
| 2 | Macro F1 and per-label F1 | macro F1 at least 0.50, and F1 at least 0.50 for `opinion`, `news` and `result`, on all three seeds | MISSED | Macro F1, `news` and `result` pass on every seed. `opinion` is 0.200, 0.222, 0.222, so the criterion fails on all three. |
| 3 | Balance | no label above 50% or below 12% of `labels.csv` | MET | `result` 32%, `opinion` 24%, `analysis` 22%, `news` 22%. |
| 4 | Agreement with staff | at least 21 of 30 | MET | 28 of 30 (93%). |
| 5 | Confidence | mean confidence higher when right than wrong, and accuracy at least 0.60 in the most confident third, on all three seeds | MET | Right 0.576 / 0.573 / 0.582 against wrong 0.471 / 0.447 / 0.477. Top third 0.90 on every seed. |

I did not revise any criterion. Criterion 2 was measurable and I missed it.

**Diagnoses**

**Criterion 2, `opinion` F1 of 0.20 to 0.22 on every seed.** My cause is a boundary I defined by absence and applied inconsistently, not too few examples. I know four things.

- Not too few examples: `opinion` has 49 rows (24%), more than `analysis` with 46 (22%), and `analysis` reached F1 0.857, 0.500 and 0.750. A label with more rows than a label that worked is not starved.
- Not one hard pair: `opinion` recall is 1 of 8 on every seed, but the misses land in different places: 6 of 8 went to `result` on seed 42, 5 of 8 to `analysis` on seed 7, and on seed 2024 they scattered across `result` (3), `analysis` (2) and `news` (2). A hard pair would lose to the same neighbor each time. Here the model has no consistent signal for `opinion`, which fits a label whose definition is "a mood, joke or view with nothing checkable behind it": it is mostly what the post lacks.
- My own hard cases show the inconsistency: two of my three hard cases (the `$2` bill post and the mean-reversion post) are `opinion` posts that name numbers or mechanisms, and I kept them out of `analysis` by reading intent (satire, challenging other traders) instead of the text. That rule makes `opinion` contain posts that look like `analysis` on the surface, which a 144-post model cannot separate.
- The agreement report shows the same lean: on the staff set my two disagreements were `hot_take` and `reaction` where staff said `analysis`. In both, a checkable fact was doing the work and I let tone outvote it. Both landed in pile (a), a rule I applied loosely. That is the same direction as my `opinion` hard cases: I under-credited support. The staff set is not my 207 labels, and my 28 of 30 shows I apply a written rule well when I follow it, so this points to my `opinion` versus `analysis` call being the weak spot, not to labeling in general.

What I have not tested: I have not re-read the 49 `opinion` rows against the "fact carries the argument" test, so I do not know how many are mislabeled. Seed spread also matters here (one post is about 3 points), but `opinion` at 0.20 to 0.22 on all three seeds is too stable to be noise. If the re-read finds few mislabeled rows, the cause is closer to a label the model cannot learn from this much data.

---

## Agreement Report

<!-- Your rate against the staff set, and every disagreement adjudicated.

     Remember you labelled these 30 under the STAFF taxonomy in
     data/staff_taxonomy.md, not your own — so every argument below is made
     from those definitions and those decision rules. -->

**Agreement rate:** 28 / 30 = 93%

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
> *The post:* "The club championship scoring changed in 2019 from top-6 to top-10. Since then our B team has finished above the A team twice. That's not depth improving, it's the scoring rewarding turnout."
>
> *Staff said / I said:* `analysis` / `hot_take`
>
> *My call, and why:* Staff is right. I read the confident last sentence as a conclusion reached first. But the post gives a dated rule change and a countable result, and "since then" makes them the reason for the conclusion. Under Rule 1 that is a load-bearing fact, not a flourish. Two events is a thin sample, but Rule 1 asks whether the fact carries the argument, not whether the argument is strong.
>
> *Which pile:* (a) The rule covered it and I applied it loosely.

**2.**
> *The post:* "Three of us ran the same session on the same day, different shoes, within 10 seconds of each other over 5 miles. I'm not saying shoes do nothing, but whatever they do was smaller than the noise between three people."
>
> *Staff said / I said:* `analysis` / `reaction`
>
> *My call, and why:* Staff is right, though my reading was not careless. The post is about the writer's own recent run, which fits the "writer's experience" half of `reaction`. But the definition says `reaction` is feeling rather than argument, and this post has no feeling in it. It argues from a checkable measurement (10 seconds over 5 miles, three runners) to a conclusion about shoes. Rule 3 settles it: recency does not outrank evidence.
>
> *Which pile:* (a) The rule covered it and I applied it loosely.

**What the pattern in my disagreements tells me:**

Both misses went the same way: I kept a post out of `analysis` because of its surface (a confident closing line, a first-person setting) when the facts were doing the work. Both are pile (a), so my reading of Rule 1 and Rule 3 was inconsistent. I should test for a load-bearing fact before looking at tone, and I should check the same thing across my own 200 labels.



---

## The Improvement

**What I changed:** I relabeled one boundary, `opinion` versus `analysis`, and nothing else. I applied one rule across all 49 `opinion` rows: if a checkable number, event or causal mechanism carries the argument, the post is `analysis`, even when the tone is heated or joking. Four rows changed from `opinion` to `analysis` (rows 43, 58, 77 and 88 of `labels.csv`, each with a note). Rows I left alone on purpose: the satire posts (18, 153) and the loose-reasons hard case (32). The file is now `result` 67, `analysis` 50, `opinion` 45, `news` 45. Training settings, epochs and seeds are unchanged.

**Which diagnosis pointed at it:** The Milestone 4 diagnosis for the `opinion` miss (F1 0.20 to 0.22 on every seed). It named an `opinion` versus `analysis` boundary I applied by intent, not by whether a fact carried the argument, and my agreement report showed the same lean on the staff set.

### Run Log — After

Numbers come from `results_three_seeds_after.json` (10 epochs, learning rate 2e-5, same three seeds).

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1. Accuracy | at least 0.60 on all three seeds | 0.812 | 0.625 | 0.719 | MET |
| 2. Macro F1 and per-label F1 | macro F1 at least 0.50, and F1 at least 0.50 for `opinion`, `news` and `result`, on all three seeds | macro 0.795<br>`opinion` 0.600<br>`news` 0.923<br>`result` 0.833 | macro 0.585<br>`opinion` 0.250<br>`news` 0.769<br>`result` 0.706 | macro 0.643<br>`opinion` 0.250<br>`news` 0.824<br>`result` 0.833 | MISSED. `opinion` passes on seed 42 only (0.600) and fails on seeds 7 and 2024 (0.250). |
| 3. Balance | no label above 50% or below 12% of `labels.csv` | 32% to 22% | same file | same file | MET (`result` 32%, `analysis` 24%, `opinion` 22%, `news` 22%) |
| 4. Agreement with staff | at least 21 of 30 | 28 of 30 | same file | same file | MET (93%, unchanged, since the staff set was not retrained) |
| 5. Confidence | mean confidence higher when right than wrong, and accuracy at least 0.60 in the most confident third, on all three seeds | right 0.556, wrong 0.387<br>top third 1.00 | right 0.597, wrong 0.410<br>top third 1.00 | right 0.582, wrong 0.452<br>top third 1.00 | MET |

Before and after, side by side:

| Measure | Seed 42 before / after | Seed 7 before / after | Seed 2024 before / after |
|---|---|---|---|
| Accuracy | 0.750 / 0.812 | 0.625 / 0.625 | 0.719 / 0.719 |
| Macro F1 | 0.707 / 0.795 | 0.585 / 0.585 | 0.648 / 0.643 |
| F1 `opinion` | 0.200 / 0.600 | 0.222 / 0.250 | 0.222 / 0.250 |
| F1 `analysis` | 0.857 / 0.824 | 0.500 / 0.615 | 0.750 / 0.667 |
| F1 `result` | 0.769 / 0.833 | 0.762 / 0.706 | 0.870 / 0.833 |
| F1 `news` | 1.000 / 0.923 | 0.857 / 0.769 | 0.750 / 0.824 |

Spread across seeds, before then after: accuracy 0.125 to 0.188, macro F1 0.121 to 0.210, `opinion` F1 0.022 to 0.350.

**Did it help, and how do I know:** Only partly, and on one seed. On seed 42 `opinion` F1 went from 0.200 to 0.600 and accuracy from 0.750 to 0.812, which clears the 0.50 `opinion` line there for the first time. On seeds 7 and 2024 accuracy did not move and `opinion` F1 went from 0.222 to 0.250, a gain of about one post that still fails the criterion. Macro F1 on seed 2024 slipped by 0.005, and `analysis`, `result` and `news` F1 each went down on at least one seed. Criterion 2 is still MISSED, because the target has to hold on all three seeds.

I cannot call the seed 42 jump proof that the relabel worked. Only 4 of 207 rows changed, `opinion` has about 8 test posts per seed, so one post is 12 to 14 points of `opinion` recall, and the three seeds disagree. The seed 42 test set also changed: its confusion matrix now has 7 `opinion` and 8 `analysis` posts (before: 8 and 7), so one of my four relabeled rows landed in that test split, and the before and after scores there are not on identical labels. Seed 42 after: 3 of 7 `opinion` posts are right, 3 went to `result` and 1 to `analysis`, and 0 `result` posts were called `opinion`. The lopsided direction is the same as before (6 of 8 went to `result`), so the relabel did not remove the lean toward `result`. The honest reading is that the relabel moved the right label in the right direction on every seed, by a large amount on one, and did not fix the label.

**The spread is now a finding of its own.** Accuracy moved 0.188 across seeds, and macro F1 moved 0.210, both well over the ten-point mark for a stable measure. It was already over it before (0.125 and 0.121), and the relabel made it worse, because one seed improved and two did not. The test split is 32 posts and `opinion` has 8 of them, so a few posts decide each verdict. My dataset is too small for these per-label criteria to give a stable answer, and a single relabel cannot be told apart from split noise at this size. I would need more posts, or more seeds, before I trusted any one run.

---

## What's Still Broken

**Criterion 2 (per-label F1), still MISSED.** `opinion` F1 is 0.600, 0.250 and 0.250, so it passes on seed 42 only. What I would do next: have a second reader label the 45 remaining `opinion` rows blind, count how many flip to `analysis`, and add about 30 new `opinion` posts that are plainly mood or joke with no checkable support. I stopped because this unit allows one change, and four relabeled rows did not settle the boundary. On seeds 7 and 2024 only 1 of 7 `opinion` posts is right, and on seed 7 five of the seven went to `analysis`, so the leftover `opinion` rows still look like `analysis` to the model.

Criteria 1, 3, 4 and 5 are met. The spread (accuracy 0.188, macro F1 0.210) is not a criterion, but I would not trust any single seed until I have more test posts.

**The gap between what I meant my labels to capture and what the model learned:**

I meant `opinion` to be a mood or joke with nothing checkable behind it, but I defined it by what it lacks, so the model never found a signal of its own for it. In the confusion matrices `opinion` is the one label whose misses go to different places, and on seed 42 3 of 7 still went to `result` while 0 `result` posts were called `opinion`.

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
