drop table IF EXISTS mimiciv_derived_sepsis.sepsis_inputeventsneeded;
drop table IF EXISTS mimiciv_derived_sepsis.sepsis_action_inputevents;

create table mimiciv_derived_sepsis.sepsis_inputeventsneeded as
	select stay_id, itemid, starttime, endtime, amount
	from mimiciv_icu.inputevents
	where itemid = 220964 	--Dextrose_5%_Saline_0_9%, No data
		or itemid = 220954 	--Saline_0_9%, No data
		or itemid = 225158 	--NaCl_0_9%, 1258660 rows
		or itemid = 220949 	--Dextrose_5%, 1034251 rows
		or itemid = 221906	--Norepinephrine
		or itemid = 222315	--Vasopressin
		or itemid = 221653	--Dobutamine
		or itemid = 221986 	--Milrinone
		or itemid = 221749 	--Phenylephrine
		or itemid = 221662 	--Dopamine
		or itemid = 221289 	--Epinephrine
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

-- create the sepsis_action_inputevents table with rows and amount of input only within the 24 hours before and 48 hours after infection time
CREATE TABLE mimiciv_derived_sepsis.sepsis_action_inputevents AS
SELECT 
    si.stay_id AS stay_id,
	si.itemid AS itemid,
    GREATEST(si.starttime, it.infection_start_time) AS starttime, -- limit the start time to the infection start time (24 hours before infection time)
    LEAST(si.endtime, it.infection_end_time) AS endtime, -- limit the end time to the infection end time (48 hours after infection time)
    si.amount * EXTRACT(EPOCH FROM LEAST(si.endtime, it.infection_end_time) - GREATEST(si.starttime, it.infection_start_time)) / EXTRACT(EPOCH FROM si.endtime - si.starttime) AS amount -- linearly scale the amount of input to limit the amount of input to the 24 hours before and 48 hours after infection time
FROM 
    mimiciv_derived_sepsis.sepsis_inputeventsneeded AS si
JOIN 
    temp_infection_times AS it ON si.stay_id = it.stay_id
WHERE 
    si.stay_id IN (SELECT stay_id FROM mimiciv_derived_sepsis.sepsis_patients_cohort) AND
    si.starttime <= it.infection_end_time AND
    si.endtime >= it.infection_start_time;
