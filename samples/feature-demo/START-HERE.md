# Receipt IQ fictional feature demo

All receipts are fictional. Use a separate test account to keep these out of your real spending.
Currency: INR. PNG files are uploaded individually; TXT companions are answer keys, not uploads.

## Quick walkthrough (six uploads)
1. Set your account currency to INR.
2. Upload and CONFIRM 01 through 05 in order. Review dates, amounts, quantities and units; choose Groceries for each.
3. Upload 31-investigate-this.png last. Review the extracted values against its TXT answer key; choose Groceries and confirm.
4. Open its investigation. Click billing/price alerts to highlight related receipt lines; try View evidence, Mark as expected, Dismiss, and report export.
5. Upload the SAME 31 PNG again to try duplicate detection. Confirming both intentionally increases totals; do this only in a test account.

## Full history walkthrough
Before uploading 31, confirm ALL 01 through 30 in numerical order. These span July through October and meet the Isolation Forest threshold of 30 earlier receipts. A model alert is not guaranteed merely by reaching the threshold.
Optional 32-34 add chart categories; review and choose Dining, Transport, and Health respectively. They also add merchant diversity.
Visit Dashboard and Insights: compare monthly/category spending, merchant totals, daily running totals, weekday averages, date filters, product trends and the values table. Search/filter the Library and export a report.

## Main receipt answer key and intended findings
- Item sum: 1520.00; printed subtotal: 1450.00 (difference -70.00).
- 1450.00 + 72.50 tax + 300.00 fee - 50.00 discount + 0.50 rounding = 1773.00. Printed total 1900.00 differs by +127.00.
- Bread appears twice with identical quantity and amount; may be intentional.
- Fee is 20.69% of the subtotal, above the 15% review threshold.
- Milk: historical 60.00/l versus current 90.00/l (+50%). Rice also demonstrates kg normalization and a price increase; Bread increases from 40.00 to 70.00 (+75%).
- Coffee Bean versus Coffee Beans offers an uncertain product match. Confirm only for this fictional demonstration, then inspect its price comparison.
- Main total is over 6 times the typical grocery receipt, provided at least five baseline receipts are confirmed in the same category/currency.
- First receipt intentionally has insufficient history. This is the correct state, not an error.

OCR may misread any receipt. Correct fields before confirmation; keep original values initially to explore alerts. Later correct subtotal to 1520.00 and total to 1843.00 to reconcile arithmetic while retaining the repeated item and fee. Correcting quantities or removing items requires recalculating these totals.

No single receipt exercises every feature: authentication/settings are separate, price/spending models require history, and these clear PNGs do not deliberately trigger low-confidence OCR, invalid-file handling, or the PDF upload path. Existing samples/fictional-receipt.pdf can test PDF upload separately. These are test scenarios, not claims of fraud or AI accuracy.
