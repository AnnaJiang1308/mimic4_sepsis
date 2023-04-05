/*create table A31831386
SELECT distinct charttime FROM Charteventsneeded
where stay_id=31831386;/*


/*itemid= 220235*/

/*alter table A31831386 add column id220235 text;*/

/*create view containeer as
select * from Charteventsneeded
where stay_id=31831386 and itemid = 220235;*/

update A31831386
join containeer a on A31831386.charttime = a.charttime
set id220235= value;



/*select charttime from A31831386;*/