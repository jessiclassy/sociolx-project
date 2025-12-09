import re
import pandas as pd
from yaml import safe_load
from glob import glob
import os

INTERVIEWER_RE = re.compile(r"^\d+\t((M|m)isc|[A-Z]{3}_(I|i)nt_)")
OVERLAP_RE = re.compile(r"(\[.+\])")

def string_to_compiled_pat(pat_string):
    return re.compile(
        fr"({pat_string})",
        re.IGNORECASE
    )

def create_patterns(
        yaml_path: str = "config/patterns.yaml"
    ):
    # initialize patterns
    pattern_regex = dict()

    # load YAML with patterns for regex
    with open(yaml_path) as f:
        pattern_types = safe_load(f)
    
    ######################### PREPARE PREFIX COMPONENTS ########################
    # pronoun prefix
    pron_prefix = fr"({'|'.join(pattern_types['pron'])})"

    # copula q-form prefix
    copula_prefix = fr"({'|'.join(pattern_types['copula'])})"

    # contracted copula q-form prefix
    contracted_copula_prefix = fr"({'|'.join(pattern_types['contracted_copula'])})"

    # general form prefixes
    # q_form_prefix = phrase_boundary_prefix + fr"({pron_prefix}|{contracted_copula_prefix})"
    # # copula_q_form_prefix = q_form_prefix + copula_prefix + " "
    q_form_copula_prefix = fr"{pron_prefix} {copula_prefix}\b"

    q_form_contracted_copula_prefix = fr"{contracted_copula_prefix}\b"

    pattern_regex["contracted"] = string_to_compiled_pat(q_form_contracted_copula_prefix)
    pattern_regex["copula"] = string_to_compiled_pat(q_form_copula_prefix)
    return pattern_regex

def main():
    """
    Given a sister directory of CORAAL plaintext transcripts, extract all lines
    containing copula forms within certain regular expression
    constraints. 
    """
    # Initialize list of lists
    data = []

    # Initialize regular expressions
    c_form_regex = create_patterns()
    for c in c_form_regex.keys():
        print(c_form_regex[c].pattern)
    # glob over each text file
    total = 0
    spkr_total = 0
    for f in glob("data/*_textfiles_*/*.txt"):
        
        # store filename as speaker code
        source_name = os.path.basename(f)[:-4]
        
        # store region name
        region_id = source_name[0:3]
        
        # read over the lines of the file, filtering against interviewer content
        lines = open(f, mode="r").readlines()[1:] # ignore first line with column names
        
        # now iterate over each line and check for quotatives before storing
        for line in lines:
            total += 1
            utt_id, speaker_id, _, content, _ = line.split("\t")

            # Extract target speaker's speech when overlapping with interviewer
            if not INTERVIEWER_RE.match(line):       
                spkr_total += 1     
                if content != None:
                    # search for all quotative forms
                    for c in c_form_regex.keys():
                        # find all form matches
                        patterns_found = re.findall(c_form_regex[c], content)
                        forms_found = [p[0] for p in patterns_found]

                        # check if forms exist
                        if len(forms_found):
                            data.append([
                                source_name,
                                speaker_id,
                                content,
                                utt_id,
                                region_id,
                                c, # the copula type
                                forms_found # the target column
                            ])
    
    print(f"Examined {spkr_total}/{total} lines")
    #### Convert to DataFrame to print brief overview of counts
    df = pd.DataFrame(data, columns=["source_file", "speaker_id", "utterance", "utt_id", "region_id", "c_type", "target"])

    # Explode target lists into singleton instances with duplicated metadata
    df = df.explode('target')

    print(f"Extracted {len(df)} data points")
    print(f"Counts by region:\n\n{df.region_id.value_counts()}")
    print(f"Counts by copula type:\n\n{df.c_type.value_counts()}")
    
    # create output folder if not exists
    if not os.path.exists("output/"):
        os.mkdir("output/")

    # write data to output
    df.to_csv(f"output/detected_copulars.csv")
    return

if __name__ == "__main__":
    main()