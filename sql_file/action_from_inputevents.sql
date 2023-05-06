SET search_path TO mimiciv_derived, mimiciv_hosp, mimiciv_icu, mimiciv_ed;

drop table IF EXISTS Inputeventsneeded;
drop table IF EXISTS sepsis_action;

create table mimiciv_derived.Inputeventsneeded as
	select * from mimiciv_icu.inputevents
	where itemid= 220964 or itemid= 221906 or itemid= 222315 or itemid= 221653 or itemid= 221986 or itemid= 221749;

create table mimiciv_derived.sepsis_action as
	select * from mimiciv_derived.Inputeventsneeded
	where stay_id in (select stay_id from mimiciv_derived.sepsis3);
	
	