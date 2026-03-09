# Deal Scout Arbitrage Bot

## Purpose
Deal Scout is an automated arbitrage project that will eventually scan online marketplaces and retail sources for discounted or underpriced items, compare them against resale value references, estimate profit and ROI, and send alerts through Telegram.

## Current Status
Phase 1 is complete.

### Phase 1 completed
- GitHub Actions workflow is running successfully
- Telegram alerts are working
- Project can send scheduled status messages
- EST/ET timestamp formatting is working

## Current Goal
Build Phase 2, which focuses on creating the internal structure for:
- category watchlists
- reference resale pricing
- product normalization
- scoring and filtering logic

## Project Vision
The long-term goal is to identify potentially profitable flips across:
- retail stores
- online stores
- marketplaces

The system should eventually:
1. discover candidate products
2. normalize product details
3. compare against reference resale prices
4. estimate profit, fees, shipping, and ROI
5. send alerts only for worthwhile opportunities

## Main Files
- `scanner.py` → main runner script
- `.github/workflows/daily_scan.yml` → GitHub Actions schedule
- `watchlist.json` → tracked categories and thresholds
- `price_reference.csv` → historical/reference resale pricing
- `ROADMAP.md` → phase-by-phase development plan

## Initial Categories
- LEGO
- Power tools
- Pokemon cards
- Small appliances
- Electronics accessories

## Notes
Phase 1 currently acts as a stable system health check.

Phase 2 will not focus on scraping every website at once. Instead, it will focus on building a cleaner internal engine:
- watchlists
- price memory
- profit rules
- category logic

This approach will make later scraping and deal validation much easier and more reliable.
