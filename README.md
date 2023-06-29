mimic4_spesis
===============

TODO: Write a project description here

# To-Do List

## As of 2023-06-29

### Hanxi Jiang 

- ~~Average or sum up the data in the state space per hour.~~
- Add the environment calculating the reward regarding the end of each patient’s trajectory.
- ~~Data concerned with patient attributes (weight, gender, age) could be selectly picked in advance, you will find them in `itemid_info/PatientAttribute.csv`.~~

### Xuyuan Han 

- ~~Filter data from up to 24 h preceding until 48 h following the estimated onset of sepsis.~~
- ~~Filter stayid on withdrawal of treatment.~~
- ~~Check *vassopressor was not administered to every stayid.*~~
- ~~Address patients who did not have recorded vital signs for more than 6 hours *within 72 hours*.~~

# Getting Started

## 1. Load MIMIC-IV into a PostgreSQL database 
Refer to [Github](https://github.com/MIT-LCP/mimic-code/tree/main/mimic-iv/buildmimic/postgres)

## 2. Generate useful abstractions of raw MIMIC-IV data ("concepts") 
Refer to [Github](https://github.com/MIT-LCP/mimic-code/tree/main/mimic-iv/concepts_postgres)

## 3. Create conda environment and install required packages

```shell
conda create --name mimiciv_sepsis python=3.11
conda activate mimiciv_sepsis
pip install -r requirements.txt
```

## 4. Run [01_data_preprocessing.ipynb](/01_data_preprocessing.ipynb) to preprocess the data for Reinforcement Learning

- Extract data from the original mimiciv database
  - Select `sepsis_patients_cohort` from `mimiciv_derived.sepsis3` 
    - Refer to [select_patients_cohort.sql](/sql/select_patients_cohort.sql) for extraction methods
    - ***Inclusion criteria:***
      - patients meeting sepsis-3 definition
      - only the first ICU visit per each patient
      - patients over the age 18
      - patients initially admitted to the Medical Intensive Care Unit (MICU) for the homogeneity of our patient cohort
      - data up to 24 hours before and 48 hours after the presumed sepsis onset
    - ***Exclusion criteria:***
      - patients who stayed less than 12 hours in icu
      - patients who did not have recorded vital signs for more than 6 hours
      - patients who died within 24 hours of the end of the data collection period (Withdrawal of treatment, see [Article](https://doi.org/10.1038/s41591-018-0213-5))
  - Extract `state space data` for each patient 
    - See [itemid_label_state.csv](/itemid_info/itemid_label_state.csv) for details
      - Vital signs: 
        - Sourced from `mimiciv_icu.chartevents` 
        - Refer to [state_from_chartevents.sql](/sql/state_from_chartevents.sql) for extraction methods
  - Extract `action space data` for each patient 
    - See [itemid_label_action.csv](/itemid_info/itemid_label_action.csv) for details
      - IV_fluid_bolus: 
        - Sourced from `mimiciv_icu.inputevents` 
        - Refer to [action_from_inputevents.sql](/sql/action_from_inputevents.sql) for extraction methods
      - Vasopressors_equivalent_dose: 
        - Sourced from `mimiciv_derived.norepinephrine_equivalent_dose` 
        - Refer to [action_from_vasopressors_equivalent_dose.sql](/sql/action_from_vasopressors_equivalent_dose.sql) for extraction methods
  - Transfer the extracted data into `pandas.DataFrame` and save them as `csv` files
    - Refer to [data_transfer.py](/python/data_preprocessing/data_transfer.py) for details
- `One-hour resample` extracted data
  - Refer to [hourly_sample.py](/python/data_preprocessing/hourly_sample.py) for resampling methods
  - Hourly sample `state space` (patient records)
  - Hourly sample `action space` (patient input) and obtain `discrete action space` 
    - `Discrete action space` is obtained by discretizing the continuous action space with the following rules (see [Article](https://doi.org/10.1038/s41591-018-0213-5)):
      | Discretized Level   | IV fluids (mL/1 hours)   |              | Vasopressors (mcg/kg/min)   |              |
      |---------------|---------------------------------|--------------|-----------------------------|--------------|
      |               | Range                           | Median dose  | Range                       | Median dose  |
      | 1             | 0                               | 0            | 0                           | 0            |
      | 2             | ]0-12.5]                        | 7.5          | ]0-0.08]                    | 0.04         |
      | 3             | ]12.5-45]                       | 21.25        | ]0.08-0.22]                 | 0.13         |
      | 4             | ]45-132.5]                      | 80           | ]0.22-0.45]                 | 0.27         |
      | 5             | >132.5                          | 236.5        | >0.45                       | 0.68         |