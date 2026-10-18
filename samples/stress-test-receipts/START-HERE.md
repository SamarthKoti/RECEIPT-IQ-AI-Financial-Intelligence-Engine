# Long receipt challenge pack

FICTIONAL DATA ONLY. Use a separate test account, INR currency, and Groceries for comparisons. No records have been added to the app.

## Upload order
Upload and review/confirm 01-05 first (60 items each). Then upload 06 (120 items). Five prior same-category purchases enable statistical spending comparison and price history. These five do NOT enable Isolation Forest, which needs 30 earlier receipts. You may use the earlier feature-demo history pack for that branch, but mixing histories changes comparisons.

## Challenges
- 06: 120 line items, large total, two deliberate repeated item pairs, subtotal short by 349.75, unexplained final excess of 499.99, high service charge, two taxes, discount and negative rounding. Milk: 60 per litre to 90 (+50%). Rice: 100 per kg to 190 (+90%), using grams on the new receipt. Coffee Bean versus Coffee Beans tests uncertain matching. Other price rises are intentionally large.
- 07: 100 items with CORRECT arithmetic. A control to test false positives. History-based alerts may still occur; arithmetic should reconcile after accurate extraction.
- 08: 90 items with alternating pale print. Arithmetic is correct; this challenges OCR. A low-confidence warning is not guaranteed.
- 09: 80 real items, eight wrapped description/amount pairs, similar but distinct coffee products, and product names containing Discount, Round, and Tax. Arithmetic is correct. This deliberately challenges the current line-based parser: it may lose product names or misclassify products as adjustments. Review and correct using JSON; do not treat parser errors as real billing faults. Do not confirm different coffee products as identical simply because their names look similar.
- Upload the SAME 06 PNG again for duplicate transaction testing. Both confirmed copies inflate totals; only do this in a test account.

## How to assess results
Each PNG has a TXT copy of printed text and a JSON answer key with every item, quantity/unit, tax, fee, discount, rounding and expected total. TXT/JSON are for review; upload only PNGs individually, not the ZIP.

First record what OCR extracts without corrections. Compare item counts, names, quantities, units, amounts, and totals to JSON. Then correct the extracted fields and confirm to assess the calculation/price engines independently from OCR errors. Explore evidence highlighting, expected/dismissed alert states, corrections, reports, Library search/filtering and Insights charts. Do not assume all alerts must fire or that no alert means a flawless receipt.

All images are below the current 25-megapixel limit. Long OCR can take time or reach the app's timeout; that is a useful stress result, not proof of fraud. These are single PNG receipts; PDF and invalid-file flows are separate tests. Five historical examples establish comparison eligibility, not a reliable real-world spending profile.
