mimic4_spesis
===============

# TODO

## 2023-06-19

### Hanxi Jiang 

 - average or sum up the data in the state space per hour
 - add another filter in the step *hourly sample* to drop the feature with too many missing values
 - add the environment calculating the reward regarding to the end of each patient’s trajectory

### Xuyuan Han 

 - ~~filter data from up to 24 h preceding until 48 h following the estimated onset of sepsis~~
 - filter stayid on withdrawal of treatment
 - check *vassopressor was not administered to every stayid*

# here are the steps up to now

1. bulid the sql environment with Postgresql, code could be found [here](https://github.com/MIT-LCP/mimic-code/tree/main/mimic-iv/buildmimic/mysql).

2. data concerned to patient attributes (weight, gender, age) could be selectly picked in advance, you will find them in `itemid_info/PatientAttribute.csv`

