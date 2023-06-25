DROP SCHEMA IF EXISTS mimiciv_derived_sepsis CASCADE;
CREATE SCHEMA mimiciv_derived_sepsis;

DROP TABLE IF EXISTS mimiciv_derived_sepsis.sepsis_patients_cohort;
DROP TABLE IF EXISTS temp_infection_times;

-- create temporary table containing stay_id, end of the data collection period
CREATE TEMPORARY TABLE temp_infection_times AS
SELECT 
    subject_id, 
    stay_id,
    suspected_infection_time + INTERVAL '48 hours' AS collection_end_time,
    suspected_infection_time - INTERVAL '24 hours' AS collection_start_time,
    ROW_NUMBER() OVER (PARTITION BY subject_id ORDER BY suspected_infection_time DESC) AS rn
FROM 
    mimiciv_derived.sepsis3;

CREATE TABLE mimiciv_derived_sepsis.sepsis_patients_cohort AS
	SELECT * FROM mimiciv_derived.sepsis3
	WHERE
	    -- remove patients who stayed less than 12 hours in icu 
	    stay_id NOT IN (SELECT stay_id FROM mimiciv_derived.icustay_hourly GROUP BY stay_id HAVING MAX(hr) - MIN(hr) < 12)
	
	    -- remove patients who did not have recorded vital signs for more than 6 hours within the 72 hour time period around sepsis onset
	    AND stay_id NOT IN (
	      SELECT stay_id 
	      FROM 
	          (SELECT c.stay_id, c.charttime, LAG(c.charttime) OVER (PARTITION BY c.stay_id ORDER BY c.charttime) AS previous_charttime 
	           FROM mimiciv_icu.chartevents c
	           INNER JOIN temp_infection_times t ON c.stay_id = t.stay_id
	           WHERE c.charttime BETWEEN t.collection_start_time AND t.collection_end_time) AS subquery
	      WHERE previous_charttime IS NOT NULL AND EXTRACT(EPOCH FROM (charttime - previous_charttime))/3600 > 6)
	  
	    -- include only patients over age 18
	    AND subject_id IN (SELECT subject_id FROM mimiciv_derived.age WHERE age >= 18)
	
	    -- include only patients initially admitted to the Medical Intensive Care Unit (MICU) 
	    AND subject_id IN (SELECT subject_id FROM mimiciv_icu.icustays WHERE first_careunit = 'Medical Intensive Care Unit (MICU)')

	    -- include only first icu visit per each patient 
	    AND stay_id IN (
	    	SELECT stay_id 
	    	FROM (SELECT stay_id, ROW_NUMBER() OVER (PARTITION BY subject_id ORDER BY suspected_infection_time) AS rn FROM mimiciv_derived.sepsis3) AS subquery
			WHERE rn = 1)

	    -- exclude patients who died within 24 hours of the end of the data collection period
		AND stay_id NOT IN (
		  	SELECT t.stay_id
		  	FROM temp_infection_times t
		  	JOIN mimiciv_hosp.patients p ON p.subject_id = t.subject_id
		  	WHERE t.rn = 1 AND p.dod IS NOT NULL AND p.dod BETWEEN t.collection_end_time AND t.collection_end_time + INTERVAL '24 hours')
	;