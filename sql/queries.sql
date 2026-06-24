-- 1 Top 5 funds by AUM
SELECT * FROM aum
ORDER BY total_aum_crore DESC
LIMIT 5;

-- 2 Average NAV per month
SELECT strftime('%Y-%m', date) month,
AVG(nav) avg_nav
FROM nav_history
GROUP BY month;

-- 3 SIP growth
SELECT *
FROM sip;

-- 4 Transactions by state
SELECT state,
COUNT(*) total_transactions
FROM transactions
GROUP BY state;

-- 5 Funds with expense ratio below 1%
SELECT scheme_name,
expense_ratio_pct
FROM scheme_performance
WHERE expense_ratio_pct < 1;

-- 6 Fund count by category
SELECT category,
COUNT(*)
FROM fund_master
GROUP BY category;

-- 7 Fund count by fund house
SELECT fund_house,
COUNT(*)
FROM fund_master
GROUP BY fund_house;

-- 8 Average investment amount
SELECT AVG(amount_inr)
FROM transactions;

-- 9 Highest NAV
SELECT MAX(nav)
FROM nav_history;

-- 10 Risk grade distribution
SELECT risk_grade,
COUNT(*)
FROM scheme_performance
GROUP BY risk_grade;