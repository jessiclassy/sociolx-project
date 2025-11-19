# LING 532 term project
An investigation of quotatives in the Corpus of Regional African American Language (CORAAL).

## Requirements
WIP

## Directory Structure (WIP)

```cmd
├── config
│   └── quotatives.yaml
├── data
│   ├── ATL_metadata_2020.05.txt
│   ├── ATL_textfiles_2020.05
│   ├── DCB_metadata_2018.10.06.txt
│   ├── DCB_textfiles_2018.10.06
│   ├── ROC_metadata_2020.05.txt
│   ├── ROC_textfiles_2020.05
│   ├── VLD_metadata_2021.07.txt
│   ├── VLD_textfiles_2021.07
├── LICENSE
├── preprocess.ipynb
└── README.md
```

## Data Preprocessing
This stage requires 2 inputs:
1. filepath to plaintext transcripts of CORAAL interview data, under `data/`
2. filepath to inflected quotative forms, under `config/`

The plaintext transcripts are wrangled into `pandas` `Dataframe` objects with columns:

|  name  |  source  |
|---|---|
|  `speaker_id`  |  copied from transcript  |
|  `utterance`  |  copied from transcript  |
|  `utt_id`  |  utterance position within interview transcript |
|  `region_id`  | configured separately  |

### Quotative filtering
As attested by Barbieri (2005) and Cukor-Avila (2012), the first aspect of the data to target is whether a transcripted utterance contains a quotative form with the following lemma:
 - *<say>*
 - *<go>*
 - *<tell (someone)>*
 - *<be all>*
 - *<be like>*

A manual analysis of regular expression matches indicates that there are two quotative contexts which we can examine with this transcript data:
 - before ","
 - before interjections (a user-defined set)

 Interaction with AAE zero-copula leads to non-trivial search for quotative *be like* forms, as the copula verb is realized in zero form only in cases where contraction is otherwise licensed. 

The `utterance` column of the preprocessed `Dataframe` is filtered by the presence of a quotative form. A new column, `target`, is filled with the sub-string of `utterance` which has been matched against a relevant quotative inflected form. Another new column, `quotatitve` is filled with the relevant quotative lemma form. 

## Quantitative Analysis

This stage requires a plaintext CORAAL metadata file in addition to the preprocessed utterance-level data points. The extracted quotative utterances can now be analyzed for correlation with sociolinguistic variables and relative frequencies across all quotative productions.

### Independent variable(s)
Correlational and frequency analyses are performed with respect to the following independent variables:
 - region
 - age/year of birth
 - social network ties

These independent/predictor variables are associated with different metadata details, configured in a separate user-defined file. 

### Speaker-level aggregation

Utterance-level data points are aggregated to the `speaker_id` level in `aggregate.ipynb`. In doing so, the counts of each quotative lemma form are recorded in separate columns (`q_say`, `q_go`,, `q_tell`, `q_all`, `q_like`). New columns corresponding to the independent variables are also added to the data at this point. 

### Analysis

To be implemented in `analysis.ipynb`, covers all data visualization:

#### Correlational Analysis

Aggregated quotative counts allow computation of the speaker-level rate of quotative "be like" usage with respect to all other quotative forms. This allows visual analysis of correlation between independent variables described above. 

#### Frequency Analysis

Contigency tables for each quotative lemma form and `speaker_id` values are generated to provide more context on the distribution of quotative usage across regions. 

## (TBD) Linear Classification

If time allows, training a linear classifier on the utterance-level data points for each region can help to quantify the strength of the relationship between the independent variables under investigation and quotative forms in AAE. 

A linear classifier is trained to predict the `quotative` column value, given all CORAAL metadata columns relevant to each speaker. The identifying `speaker_id`, `region_id` features are removed. The classifier's accuracy is reported to indicate the stable relationship between social metadata features and quotative forms. Additionally, the relative importance of input features can be extracted from the model to strengthen the findings from correlational and frequency analysis.