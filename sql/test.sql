-- set search_path to mimiciv_derived, mimiciv_hosp, mimiciv_icu, mimiciv_ed;
-- select count(distinct subject_id), count(distinct stay_id) from mimiciv_derived.sepsis_patients_cohort;

-- select * from mimiciv_icu.d_items where label like '%Dopamine%';
-- select * from mimiciv_icu.d_items where label like '%Saline%';
-- select * from mimiciv_icu.d_items where label like '%NaCl%';

-- select * from mimiciv_icu.d_items where label like '%Dextrose%';
-- select * from mimiciv_icu.d_items where label like '%Epinephrine%';

-- select * from mimiciv_icu.d_items where category like '%Fluids%';

-- select * from mimiciv_icu.d_items where itemid=220964; -- Dextrose 5% / Saline 0,9%
-- SELECT count(*) FROM mimiciv_icu.inputevents WHERE itemid=220964; -- Dextrose 5% / Saline 0,9%: 0 rows

-- select * from mimiciv_icu.d_items where itemid=220954; -- Saline 0,9%
-- SELECT count(*) FROM mimiciv_icu.inputevents WHERE itemid=220954; -- Saline 0,9%: 0 rows

-- select * from mimiciv_icu.d_items where itemid=220949; -- Dextrose 5%
-- SELECT count(*) FROM mimiciv_icu.inputevents WHERE itemid=220949; -- Dextrose 5%: 1034251 rows

-- select * from mimiciv_icu.d_items where itemid=225158; -- NaCl 0.9%
-- SELECT count(*) FROM mimiciv_icu.inputevents WHERE itemid=225158; -- NaCl 0.9%:  1258660 rows

-- 获取所有 Saline
-- select count(*) from mimiciv_icu.inputevents where itemid in (select itemid from mimiciv_icu.d_items where label like '%Saline%');
-- SELECT 
--     i.itemid, 
--     d.label, 
--     count(*) as count
-- FROM 
--     mimiciv_icu.inputevents as i
-- INNER JOIN 
--     mimiciv_icu.d_items as d 
-- ON 
--     i.itemid = d.itemid
-- WHERE 
--     d.label LIKE '%Saline%'
-- GROUP BY 
--     i.itemid, 
--     d.label;


-- 获取所有 Dextrose
-- select count(*) from mimiciv_icu.inputevents where itemid in (select itemid from mimiciv_icu.d_items where label like '%Dextrose%');
-- SELECT 
--     i.itemid, 
--     d.label, 
--     count(*) as count
-- FROM 
--     mimiciv_icu.inputevents as i
-- INNER JOIN 
--     mimiciv_icu.d_items as d 
-- ON 
--     i.itemid = d.itemid
-- WHERE 
--     d.label LIKE '%Dextrose%'
-- GROUP BY 
--     i.itemid, 
--     d.label;


-- 获取所有 NaCl
-- select count(*) from mimiciv_icu.inputevents where itemid in (select itemid from mimiciv_icu.d_items where label like '%Dextrose%');
-- SELECT 
--     i.itemid, 
--     d.label, 
--     count(*) as count
-- FROM 
--     mimiciv_icu.inputevents as i
-- INNER JOIN 
--     mimiciv_icu.d_items as d 
-- ON 
--     i.itemid = d.itemid
-- WHERE 
--     d.label LIKE '%NaCl%'
-- GROUP BY 
--     i.itemid, 
--     d.label;

-- select * from mimiciv_icu.inputevents where stay_id=30000484;
-- select * from mimiciv_derived.sepsis3 where stay_id=32217866;
-- select * from mimiciv_derived.sepsis3 where stay_id=31872514;