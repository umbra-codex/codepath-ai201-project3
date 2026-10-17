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
- report: says what the poster did or got, with a first-person result stated: a gain, loss or dollar figure that is the poster's own.
- news: relays what happened in the market or the world, from outside the poster.

Stretch plan: `news` is the fourth label (declare in README before starting). Cap is four labels total; a fifth is not allowed.

## Rules
- Label from text only. If title + body don't make the label clear, drop the post.
- Label by the post's main job; an opinion tail on a result post stays `report`.
- Drop rule: after applying the rules, if two labels still fit, drop the post.
- Classify by the sentiment the poster intends, not the slang term ("we're cooked" = doom, "he cooked" = praise). Both are `opinion`.
- Satire written like analysis is `opinion` (e.g. the "$2 bill deflation glitch" post).
- opinion vs analysis: checkable support present -> analysis; a stance or joke with no support -> opinion. Support must be specific and checkable (a number, a named catalyst, a stated figure). A general market adage ("when everyone is bullish it dumps") is not support, so it is `opinion`. (Replaces the "is there a because?" test.)
- report vs analysis: the poster states their own result (a first-person marker: "I'm up/down", "I lost/made", "my account", a dollar gain or loss tied to the poster) -> `report`. A bare number with no stated owner ("down 18%") is the market's move, not a result. A position plus a reason, where any number describes the market and not the poster's own result -> `analysis`. Judge by the words, not the implication ("shorted at $24, now $19" with no stated personal result is `analysis`).
- news vs opinion: an outside event is the main job -> `news`, even with an unsupported tail ("Apple announced a $110B buyback. Honestly feels like the top." is `news`).
- news vs analysis: an outside event is the whole post -> news; the event plus the poster's own causal claim -> analysis.

## Milestone 2: hardest boundary (report vs analysis)
- Post (real): "I am financially ruined (short selling Korean fried chicken companies)": "This week I lost $472,085 short selling Korean fried chicken companies. My idea was with the declining Korean population, and the recent trend towards healthier eating and vegan diets, there is an opportunity here. I did some research into consumer trends in Korea..." then a viral Jensen Huang dinner sends the stocks up 20-30% and he is margin called.
- Between: report and analysis (a full thesis, plus a personal loss)
- Rule: the poster states their own result (a first-person loss, gain or dollar figure) -> `report`, even when the post also lays out the thesis behind the trade. A position plus a reason with no stated personal result -> `analysis`.
- Link: https://www.reddit.com/r/wallstreetbets/comments/1olwc77/i_am_financially_ruined_short_selling_korean/

## Milestone 2: second boundary (report vs opinion)
- Post: 1x0a930, "POV: You always buy the top, but Al says..." (lost $225K on options, holds semi portfolio, ends "big name AI stonks only go up. HODL")
- Between: report and opinion
- Rule: if the post states what the poster did, holds or got, it is report, even with a bullish or bearish tail. A take with no personal position or result is opinion.
- Link: https://www.reddit.com/r/wallstreetbets/comments/1x0a930/pov_you_always_buy_the_top_but_al_says_relax/
- Second boundary to write up: opinion vs analysis, e.g. post 103 ("there isn't even an AI bubble... supply is not close to answering demand") labeled opinion.

## Milestone 2: definitions and examples (two per label)
- opinion: "WE ARE SO FUCKING BACK"; "The whole world has become a casino"
- analysis: "Anthropic are not going to be profitable" ($4b revenue vs $46b costs); "broad market is breaking down while top 10 big tech holds up the s&p 500 illusion" (66% of S&P stocks at 52-week lows)
- report: "69 bagger, $30k -> $2.09mil" (his own result, with an unsupported 'still believe 5-10x' tail); "Good bye Wallstreet" ($200,000 to nearly $800,000)
- news: "President Trump says he will no longer be imposing 10% tariffs on EU countries on February 1st."; "Apple sues OpenAI alleging trade secret theft, says scheme was 'at every level'"

## Milestone 2: AI stress test (8 posts written by Aurora, labeled blind by Umbra)
Matched the key 4 of 8 on first pass (3, 4, 5, 6). Misses 1, 2, 7, 8 exposed three gaps, fixed in the rules above:
- 1: "mechanism" was undefined -> support must be specific and checkable.
- 2 and 7: position plus reason labeled inconsistently -> report vs analysis rule keyed on a stated personal result. (Post 7's "down 18%" was ambiguous between his P&L and the stock; that was a flaw in the test post.)
- 8: outside event with an opinion tail -> `news`.
Final labels for the eight: 1 opinion, 2 analysis, 3 report, 4 news, 5 analysis, 6 opinion, 7 dropped (ambiguous owner of "down 18%"), 8 news.

## To do
- labels.csv at 43 rows (opinion 18, news 13, report 8, analysis 4). Need 200 total.
- analysis is thin: pull long Discussion/DD bodies. Re-check ~10 borderline rows before Milestone 4.
