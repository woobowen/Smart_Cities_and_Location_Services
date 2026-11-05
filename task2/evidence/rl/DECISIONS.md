# Result-triggered RL decisions (chronological; validation only)

## RL-D01 · trustworthy pilot to teacher-scale training

Ten actual training episodes took1.30s. Validation three sampled simulated days: greedy17069.03, KM16288.72, QKM17175.57 accepted-fare units; QKM pickup1.909km vs greedy1.559. No held-out test used. Proceed with teacher300episode40/60/100 baselines because cost fits local CPU budget.

## RL-D02 · scarcity and β rejection diagnosis

300episode60fleet validation five simulated days: QKM16830.68, KM15892.18, greedy16371.21. At100fleet QKM20636.69 < KM21197.29. This is valid method degradation, not a failing unit test. β scan using same60fleet trained table gives β.5 revenue16830.68 / response.5900 / nonpositive-edge fraction.03031, β1 revenue14127.71 / response.56813 / fraction.37721. Hypothesis: aggressive regional opportunity cost produces rejection and misplaced optimism. Proceed with predeclared DoubleQ vs Q atβ1, five paired training seeds; retain β.5 as teaching reference, no final-test tuning.

## RL-D03 · V-only movement gains gross revenue but creates large empty cost

Validation QKM+V movement revenue17245.64, response.6288, empty5005.50km per simulated day, versus no movement16830.68/.5900/0km. KM+V17885.81/.64253/5096.95km. Thus movement raises gross metrics but at the predeclared diagnostic1currency/km cost loses net value. No net-improvement claim is supported. New test: movement requires discounted V gain to exceed λ×Manhattan empty distance, λ∈{0,1,3,5}; only threshold changes, same model/days/initial drivers, true movement occupancy retained. Implemented in a separate extension to keep active training source frozen.

## RL-D04 · movement threshold controls excess travel

Same validation five days: λ0 revenue17245.64, empty5005.50km; λ1 revenue17732.72, empty1449.56km; λ3 revenue18195.76, empty701.87km; λ5 revenue18018.84, empty255.25km. λ3 maximizes gross revenue and meets the predeclared response safeguard; λ5 uses less distance and has greater diagnostic net revenue at1/km. Both are legitimate tradeoffs. Keepλ3 as gross-revenue candidate and preserveλ5 sensitivity; require parent/combination comparison with KM+λ3, then held-out confirmation after all choices frozen. These λ values are hypothetical movement-decision penalties, not estimated real vehicle costs.

No observation here is presented as an earlier user challenge or an external GPT acceptance. These are native execution/design-agent decisions within the approved dynamic research boundary.
