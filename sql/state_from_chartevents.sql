drop table IF EXISTS mimiciv_derived_sepsis.sepsis_charteventsneeded;
drop table IF EXISTS mimiciv_derived_sepsis.sepsis_state;

create table mimiciv_derived_sepsis.sepsis_charteventsneeded as
	select stay_id, charttime, itemid, valuenum 
	from mimiciv_icu.chartevents
	where itemid= 220045 or itemid= 220050 or itemid= 220179 or itemid= 220051  or itemid= 220180 
		or itemid= 220052 or itemid= 220181 or itemid= 220210 or itemid= 223761 or itemid= 223762
		or itemid= 223830 or itemid= 220274 or itemid= 224828
		;
	
insert into mimiciv_derived_sepsis.sepsis_charteventsneeded
	select stay_id, charttime, itemid, valuenum 
	from mimiciv_icu.chartevents
	where
		 itemid= 220545 or itemid= 226540 or itemid= 220228 or itemid= 227457 or itemid= 220546
		or itemid= 220602 or itemid= 226536 or itemid= 225667 or itemid= 225625 or itemid= 227442
		or itemid= 227464 or itemid= 220645 or itemid= 226534
		;
	
insert into mimiciv_derived_sepsis.sepsis_charteventsneeded
	select stay_id, charttime, itemid, valuenum 
	from mimiciv_icu.chartevents
	where
		   itemid= 227465 or itemid= 227466 or itemid= 227467
		or itemid= 220227 or itemid= 220277 or itemid= 226862 or itemid= 220235 or itemid= 223835
		or itemid= 225624 or itemid= 220615 or itemid= 229761 or itemid= 227456 or itemid= 227073
		;
	
insert into mimiciv_derived_sepsis.sepsis_charteventsneeded
	select stay_id, charttime, itemid, valuenum 
	from mimiciv_icu.chartevents
	where
		   itemid= 225690 or itemid= 225651 or itemid= 220644 or itemid= 220587
		or itemid= 227519 or itemid= 220739 or itemid= 223900 or itemid= 223901
		;

-- create temporary table containing stay_id, infection_start_time, infection_end_time
DROP TABLE IF EXISTS temp_infection_times;
CREATE TEMPORARY TABLE temp_infection_times AS
SELECT 
    stay_id, 
    suspected_infection_time - INTERVAL '24 hours' AS infection_start_time, 
    suspected_infection_time + INTERVAL '48 hours' AS infection_end_time
FROM 
    mimiciv_derived.sepsis3;

-- use the temporary table to select the chartevents needed for the state table
CREATE TABLE mimiciv_derived_sepsis.sepsis_state AS
SELECT 
    sc.*
FROM 
    mimiciv_derived_sepsis.sepsis_charteventsneeded AS sc
JOIN 
    temp_infection_times AS it ON sc.stay_id = it.stay_id
WHERE 
    sc.stay_id IN (SELECT stay_id FROM mimiciv_derived_sepsis.sepsis_patients_cohort)
    AND sc.charttime BETWEEN it.infection_start_time AND it.infection_end_time;

	
	