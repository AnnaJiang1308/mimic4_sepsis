set search_path to mimiciv_derived, mimiciv_hosp, mimiciv_icu, mimiciv_ed;

drop table if exists sepsis_patients_cohort;

create table sepsis_patients_cohort as
	select * from sepsis3
	  	  --remove patients who stayed less than 12 hours in icu 
	where stay_id not in (select stay_id from icustay_hourly group by stay_id having max(hr) - min(hr) < 12)
	
	  	  --remove patients who did not have recorded vital signs for more than 6 hours. 
	  	  --Without removal: (subject_id, stay_id):(7871, 12874). With removal: (subject_id, stay_id):(7113, 10671)
	  and stay_id not in (select stay_id from 
	  	  (select stay_id, charttime, lag(charttime) over (partition by stay_id order by charttime) as previous_charttime from chartevents) as subquery
	  	  where previous_charttime is not null and extract(epoch from (charttime - previous_charttime))/3600 > 6)
	  
		  --include only patients over age 18 
	  and subject_id in (select subject_id from age where age >= 18)
	
		  --include only patients initially admitted to the medical intensive care unit (micu) for the homogeneity of our patient cohort 
	  and subject_id in (select subject_id from icustays where first_careunit = 'Medical Intensive Care Unit (MICU)')

	  	  --include only first icu visit per each patient 
	  	  --Without removal: (subject_id, stay_id):(7113, 10671). With removal: (subject_id, stay_id):(6669, 6669)
	  and stay_id in (select stay_id from 
	  	  (select stay_id, row_number() over (partition by subject_id order by suspected_infection_time) as rn from sepsis3) as subquery
		  where rn = 1)
	;