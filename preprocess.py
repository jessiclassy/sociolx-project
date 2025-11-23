import re
import pandas as pd
from yaml import safe_load
from glob import glob
import os
from argparse import ArgumentParser

INTERVIEWER_RE = re.compile(r"^\d+\t[A-Z]{3}_(I|i)nt_")
OVERLAP_RE = re.compile(r"(\[.+\])")

def string_to_compiled_pat(pat_string):
    return re.compile(
        fr"({pat_string})",
        re.IGNORECASE
    )

def create_patterns(
        any_subject: bool, 
        copula_only: bool, 
        yaml_path: str = "config/patterns.yaml"
    ):
    # initialize patterns
    pattern_regex = dict()

    # load YAML with patterns for regex
    with open(yaml_path) as f:
        pattern_types = safe_load(f)
    
    ######################### PREPARE PREFIX COMPONENTS ########################
    # pronoun prefix
    if not any_subject:
        print("Subjects restricted to adjacent pronouns")
        pron_prefix = fr"({'|'.join(pattern_types['pron'])})"
    else:
        print("No subject restriction")
        pron_prefix = ""

    # phrase boundary prefix
    phrase_boundary_prefix = fr"\b(?<!like )(?<!as )(?:so|but|now|and )?{pron_prefix}"

    # copula q-form prefix
    copula_prefix = fr"\s({'|'.join(pattern_types['copula'])})"

    # general form prefixes
    q_form_prefix = phrase_boundary_prefix
    copula_q_form_prefix = q_form_prefix + copula_prefix + " "

    ######################### PREPARE SUFFIX COMPONENTS ########################
    # phrase boundary suffix marked by orthography
    phrase_boundary_suffix = fr"((,|-)\s)|( [<\(\/\[]{1})"

    # interjection word suffix
    intj_suffix = fr"(\s({'|'.join(pattern_types['intj'])})\s)"

    # tell object suffix
    tell_obj_suffix = r" (?!you\b)(\S+)"

    # general form suffix
    suffix = f"({phrase_boundary_suffix}|{intj_suffix})"

    ####################### BUILD QUOTATIVE REGEXES ############################
    for k in pattern_types.keys():
        # enumerate out all non-copula q_forms with morphosyntactic coda
        if k.startswith("q_"):
            pat = q_form_prefix + fr" ({'|'.join(pattern_types[k])}\b)"
            
            # Q-tell requires an object which can be any combination of non-space characters
            if k.endswith("tell"):
                pat += tell_obj_suffix
            pat += suffix
            regex = string_to_compiled_pat(pat)
            pattern_regex[k] = regex
        
    ################### BUILD COPULA-QUOTATIVE REGEXES #########################
    
    # Q: be all
    all_pat = copula_q_form_prefix + r"all" + suffix
    pattern_regex["q_all"] = string_to_compiled_pat(all_pat)
    
    # Q: be like
    like_pat = copula_q_form_prefix + r"like" + suffix
    pattern_regex["q_like"] = string_to_compiled_pat(like_pat)
    
    ### BARE COPULA Q-FORMS ######
    if not copula_only:
        print("Permitting zero instances of copula-quotatives")
        # Q: all 
        all_bare_pat = q_form_prefix + r"all" + suffix
        pattern_regex["q_all_bare"] = string_to_compiled_pat(all_bare_pat)

        # Q: like 
        like_bare_pat = q_form_prefix + r"like" + suffix
        pattern_regex["q_like_bare"] = string_to_compiled_pat(like_bare_pat)
    else:
        print("Restricting to copula instances of copula-quotatives")
    return pattern_regex

def main():
    """
    Given a sister directory of CORAAL plaintext transcripts, extract all lines
    containing probable quotative forms within certain regular expression
    constraints. Options include:
    
    --copula_only (default TRUE): ignore 'bare' variants of copula-quotatives
    --any_subject (default TRUE): allow left-adjacent strings besides pronouns
    
    """
    parser = ArgumentParser()
    parser.add_argument("--copula_only", action= "store_true")
    parser.add_argument("--any_subject", action="store_true")
    args = parser.parse_args()

    # Initialize list of lists
    data = []

    # Initialize regular expressions
    q_form_regex = create_patterns(args.any_subject, args.copula_only)

    # glob over each text file
    for f in glob("data/*_textfiles_*/*.txt"):
        
        # store filename as speaker code
        target_speaker_id = os.path.basename(f)
        
        # store region name
        region_id = target_speaker_id[0:3]
        
        # read over the lines of the file, filtering against interviewer content
        lines = open(f, mode="r").readlines()[1:] # ignore first line with column names
        
        # now iterate over each line and check for quotatives before storing
        for line in lines:
            utt_id, _, _, content, _ = line.split("\t")

            # Extract target speaker's speech when overlapping with interviewer
            if INTERVIEWER_RE.match(line):
                overlapping_speech = re.findall(OVERLAP_RE, content)
                if overlapping_speech:
                    # Override default content assignment
                    content = "|".join(overlapping_speech)
            
            if content != None:
                # search for all quotative forms
                for q in q_form_regex.keys():
                    # find all form matches
                    patterns_found = re.findall(q_form_regex[q], content)
                    forms_found = [p[0] for p in patterns_found]

                    # check if forms exist
                    if len(forms_found):
                        data.append([
                            target_speaker_id,
                            content,
                            utt_id,
                            region_id,
                            q, # the quotative type
                            forms_found # the target column
                        ])
    
    #### Convert to DataFrame to print brief overview of counts
    df = pd.DataFrame(data, columns=["speaker_id", "utterance", "utt_id", "region_id", "q_type", "target"])

    # Explode target lists into singleton instances with duplicated metadata
    df = df.explode('target')

    print(f"Extracted {len(df)} data points")
    print(f"Counts by region:\n\n{df.region_id.value_counts()}")
    print(f"Counts by quotative type:\n\n{df.q_type.value_counts()}")
    
    # create output folder if not exists
    if not os.path.exists("output/"):
        os.mkdir("output/")

    # write data to output with params
    params = vars(args)
    file_params = "_".join([k for k in params if params[k]])
    df.to_csv(f"output/coraal_q_forms_{file_params}.csv")
    return

if __name__ == "__main__":
    main()