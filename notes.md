# Working notes (not graded; feeds README and labels.csv)

## Milestone 1: community and distinctions
Community: r/wallstreetbets (public, no login, not tied to one show). Collected 372 unique posts from hot/new/top listings; read well over 40.

Three distinctions I can point at (reviewed by Isis; #2 narrowed, old #4 moved to a screening rule):
1. Some posts state what the poster did or got (a position, gain or loss). Most don't.
2. Some posts make a causal claim about why a move happened or will happen. Most just assert a stance.
3. Some posts relay an outside event. Most are about the poster or the poster's feelings.

Screening rule (data quality, not a distinction): drop a post when title + body don't leave one clear main job. The model sees only text, never images.
Dropped so far: "US markets until Tuesday", "Calls", "strait of hormuz blockade satellite photo", "Farewell to one of the greatest investors of all time", "Bull Market Turns 4" (meaning lives in the image).

## Draft labels (Milestone 2 confirms these)
- opinion: states a mood, joke or view (bullish or bearish) with no checkable support behind it.
- analysis: states a view or trade with checkable support (a number, catalyst or causal mechanism) a reader could dispute.
- report: says what the poster did, holds or got: a position, gain or loss.
- news: relays what happened in the market or the world, from outside the poster.

Stretch plan: `news` is the fourth label (declare in README before starting). Cap is four labels total; a fifth is not allowed.

## Rules
- Label from text only. If title + body don't make the label clear, drop the post.
- Label by the post's main job; an opinion tail on a result post stays `report`.
- Classify by the sentiment the poster intends, not the slang term ("we're cooked" = doom, "he cooked" = praise). Both are `opinion`.
- Satire written like analysis is `opinion` (e.g. the "$2 bill deflation glitch" post).
- opinion vs analysis: checkable support present -> analysis; a stance or joke with no support -> opinion. (Replaces the "is there a because?" test; a lived position is `report`, not support.)
- news vs analysis: an outside event is the whole post -> news; the event plus the poster's own causal claim -> analysis.

## Milestone 2: boundary candidate (1 needed)
- Post: 1x0a930, "POV: You always buy the top, but Al says..." (lost $225K on options, holds semi portfolio, ends "big name AI stonks only go up. HODL")
- Between: report and opinion
- Rule: if the post states what the poster did, holds or got, it is report, even with a bullish or bearish tail. A take with no personal position or result is opinion.
- Link: https://www.reddit.com/r/wallstreetbets/comments/1x0a930/pov_you_always_buy_the_top_but_al_says_relax/
- Second boundary to write up: opinion vs analysis, e.g. post 103 ("there isn't even an AI bubble... supply is not close to answering demand") labeled opinion.

## To do
- labels.csv at 43 rows (opinion 18, news 13, report 8, analysis 4). Need 200 total.
- analysis is thin: pull long Discussion/DD bodies. Re-check ~10 borderline rows before Milestone 4.
