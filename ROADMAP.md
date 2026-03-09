# Deal Scout Roadmap

## Phase 1 – Infrastructure and Alerts
### Goal
Build a stable automation backbone.

### Completed
- GitHub repo created
- `scanner.py` created
- GitHub Actions workflow created
- Telegram bot connected
- Telegram chat ID confirmed
- Secrets configured
- EST/ET run time working
- Scheduled Telegram status message working

### Outcome
The system can run automatically and send alerts.

---

## Phase 2 – Internal Engine Skeleton
### Goal
Build the internal data model before attempting broad live scraping again.

### Tasks
- Create `watchlist.json`
- Create `price_reference.csv`
- Define category thresholds
- Define basic scoring approach
- Define product normalization goals
- Prepare the project for source-specific modules later

### Outcome
The project becomes structured and easier to expand.

---

## Phase 3 – Candidate Discovery
### Goal
Find a reliable first source of candidate products.

### Possible Approaches
- one marketplace source
- one simpler product feed or search source
- manually seeded links for testing
- category-specific source modules

### Tasks
- choose one reliable source
- extract title, price, and link
- classify into category
- pass candidates into scoring pipeline

### Outcome
The bot starts collecting real products instead of only sending system check messages.

---

## Phase 4 – Reference Pricing and Validation
### Goal
Compare candidates against known reference values.

### Tasks
- use `price_reference.csv`
- estimate average resale price
- estimate low and high resale range
- estimate fees and shipping
- calculate rough profit
- calculate ROI

### Outcome
The bot starts identifying possible profitable opportunities.

---

## Phase 5 – Alert Filtering
### Goal
Avoid spam and only send worthwhile deals.

### Tasks
- alert only if profit threshold is met
- alert only if ROI threshold is met
- require at least medium confidence
- suppress weak or duplicate alerts

### Outcome
Telegram becomes useful instead of noisy.

---

## Phase 6 – Multi-Source Expansion
### Goal
Add more buying and selling sources carefully.

### Possible Sources
- eBay
- Amazon
- Target
- Walmart
- Best Buy
- other retail or marketplace sources

### Tasks
- add source modules one by one
- normalize source-specific output
- compare sources against shared price reference model

### Outcome
The bot expands without becoming chaotic.

---

## Phase 7 – Smarter Scoring
### Goal
Improve the quality of deal recommendations.

### Future Ideas
- category-specific rules
- demand or sell-through scoring
- bundle risk penalties
- shipping difficulty penalties
- historical trend checks

### Outcome
The system becomes more accurate and more selective.

---

## Phase 8 – Full Arbitrage Agent
### Goal
Run a daily automated deal-finding pipeline.

### Final Vision
1. discover opportunities
2. normalize products
3. validate resale value
4. calculate profit and ROI
5. filter by confidence and thresholds
6. send only strong opportunities

### Desired Result
A daily Telegram digest and high-priority alerts for strong arbitrage opportunities.
