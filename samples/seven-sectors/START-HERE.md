# Seven categories, two fictional bills each

Use INR and a test account. Upload A before B within each category. Review OCR and manually choose the category named in the filename; classification is a suggestion, especially for Other and mixed utility/transport examples. Each bill is an intentionally fictional consolidated receipt, not a real supplier invoice.

A is an eight-item clean baseline. B has 66 items, including two exact repeated pairs. The first two products have quantity 2 and a 25% higher price per item than A. Printed subtotal is 137.25 below the item sum; the service charge is 20% of printed subtotal; two separate taxes, a discount and negative rounding must be accounted for. Final total is 249.99 above the printed-subtotal calculation. JSON and TXT answer keys accompany each PNG. Two bills per category are insufficient for category spending anomaly detection (minimum five earlier comparable receipts) or Isolation Forest (30 earlier receipts). Re-upload the same B image to exercise duplicate receipt detection.

- groceries-A-baseline.png: 8 items; category Groceries; item sum 800.00; subtotal 800.00; tax 40.00; fees 0.00; discount 20.00; rounding 0.00; expected total 820.00; printed total 820.00.
- groceries-B-challenge.png: 66 items; category Groceries; item sum 13331.15; subtotal 13193.90; tax 659.70; fees 2638.78; discount 120.75; rounding -0.25; expected total 16371.38; printed total 16621.37.
- dining-A-baseline.png: 8 items; category Dining; item sum 1000.00; subtotal 1000.00; tax 50.00; fees 0.00; discount 20.00; rounding 0.00; expected total 1030.00; printed total 1030.00.
- dining-B-challenge.png: 66 items; category Dining; item sum 16901.15; subtotal 16763.90; tax 838.20; fees 3352.78; discount 120.75; rounding -0.25; expected total 20833.88; printed total 21083.87.
- transport-A-baseline.png: 8 items; category Transport; item sum 1100.00; subtotal 1100.00; tax 55.00; fees 0.00; discount 20.00; rounding 0.00; expected total 1135.00; printed total 1135.00.
- transport-B-challenge.png: 66 items; category Transport; item sum 18101.15; subtotal 17963.90; tax 898.20; fees 3592.78; discount 120.75; rounding -0.25; expected total 22333.88; printed total 22583.87.
- shopping-A-baseline.png: 8 items; category Shopping; item sum 5342.00; subtotal 5342.00; tax 267.10; fees 0.00; discount 20.00; rounding 0.00; expected total 5589.10; printed total 5589.10.
- shopping-B-challenge.png: 66 items; category Shopping; item sum 89368.15; subtotal 89230.90; tax 4461.54; fees 17846.18; discount 120.75; rounding -0.25; expected total 111417.62; printed total 111667.61.
- health-A-baseline.png: 8 items; category Health; item sum 1590.00; subtotal 1590.00; tax 79.50; fees 0.00; discount 20.00; rounding 0.00; expected total 1649.50; printed total 1649.50.
- health-B-challenge.png: 66 items; category Health; item sum 26181.15; subtotal 26043.90; tax 1302.20; fees 5208.78; discount 120.75; rounding -0.25; expected total 32433.88; printed total 32683.87.
- utilities-A-baseline.png: 8 items; category Utilities; item sum 3797.00; subtotal 3797.00; tax 189.85; fees 0.00; discount 20.00; rounding 0.00; expected total 3966.85; printed total 3966.85.
- utilities-B-challenge.png: 66 items; category Utilities; item sum 62575.65; subtotal 62438.40; tax 3121.92; fees 12487.68; discount 120.75; rounding -0.25; expected total 77927.00; printed total 78176.99.
- other-A-baseline.png: 8 items; category Other; item sum 1640.00; subtotal 1640.00; tax 82.00; fees 0.00; discount 20.00; rounding 0.00; expected total 1702.00; printed total 1702.00.
- other-B-challenge.png: 66 items; category Other; item sum 27606.15; subtotal 27468.90; tax 1373.44; fees 5493.78; discount 120.75; rounding -0.25; expected total 34215.12; printed total 34465.11.