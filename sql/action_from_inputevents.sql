SET search_path TO mimiciv_derived, mimiciv_hosp, mimiciv_icu, mimiciv_ed;

drop table IF EXISTS Inputeventsneeded;
drop table IF EXISTS sepsis_action;

create table mimiciv_derived.Inputeventsneeded as
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
create table mimiciv_derived.sepsis_action as
	select * from mimiciv_derived.Inputeventsneeded
	where stay_id in (select stay_id from mimiciv_derived.sepsis_patients_cohort);
