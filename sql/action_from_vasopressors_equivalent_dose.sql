DROP TABLE IF EXISTS mimiciv_derived_sepsis.sepsis_action_vasopressors_equivalent_dose;
DROP TABLE IF EXISTS temp_infection_times;

-- create temporary table containing stay_id, infection_start_time, infection_end_time

CREATE TEMPORARY TABLE temp_infection_times AS
SELECT 
    stay_id, 
    suspected_infection_time - INTERVAL '24 hours' AS infection_start_time, 
    suspected_infection_time + INTERVAL '48 hours' AS infection_end_time
FROM 
    mimiciv_derived.sepsis3;

-- create the sepsis_action_vasopressors_equivalent_dose table with rows only within the 24 hours before and 48 hours after infection time
CREATE TABLE mimiciv_derived_sepsis.sepsis_action_vasopressors_equivalent_dose AS
SELECT 
    ne.stay_id,
    GREATEST(ne.starttime, it.infection_start_time) AS starttime,
    LEAST(ne.endtime, it.infection_end_time) AS endtime,
    ne.norepinephrine_equivalent_dose
FROM 
    mimiciv_derived.norepinephrine_equivalent_dose AS ne
JOIN 
    temp_infection_times AS it ON ne.stay_id = it.stay_id
WHERE 
    ne.stay_id IN (SELECT stay_id FROM mimiciv_derived_sepsis.sepsis_patients_cohort) AND
    ne.starttime <= it.infection_end_time AND
    ne.endtime >= it.infection_start_time;