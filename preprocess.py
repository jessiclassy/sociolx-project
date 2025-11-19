import re
import pandas as pd
from yaml import safe_load
from glob import glob
import os

INTERVIEWER_RE = re.compile(r"^\d+\t[A-Z]{3}_(I|i)nt_")

def create_patterns(yaml_path: str = "config/patterns.yaml"):
    # initialize patterns
    pattern_regex = dict()

    # load YAML with q_forms and intj strings
    with open(yaml_path) as f:
        pattern_types = safe_load(f)
    
    # prepare coda pattern - either comma or intj expression
    comma_coda = fr"(, )"
    intj_coda = fr"( ({'|'.join(pattern_types['intj'])})\b)"
    coda = f"({comma_coda}|{intj_coda})"
    
    for k in pattern_types.keys():
        # enumerate out all non-copula q_forms with morphosyntactic coda
        if k.startswith("q_"):
            pat = fr"\s({'|'.join(pattern_types[k])})"
            # Q-tell requires an object which can be any combination of non-space characters
            if k.endswith("tell"):
                pat += r" \S+"
            pat += coda
            regex = re.compile(pat, re.IGNORECASE)
            # print(regex.pattern)
            pattern_regex[k] = regex
        
    ##### COPULA Q-FORMS ######
    copula_prefix = fr"\s({'|'.join(pattern_types['copula'])}) "
    
    # Q: be all
    all_pat = copula_prefix + r"all" + coda
    pattern_regex["q_all"] = re.compile(all_pat, re.IGNORECASE)
    
    # Q: be like
    like_pat = copula_prefix + r"like" + coda
    pattern_regex["q_like"] = re.compile(like_pat, re.IGNORECASE)
    
    ### BARE COPULA Q-FORMS ######
    # pronoun prefix to constrict contexts
    pron_prefix = fr"\s({'|'.join(pattern_types['pron'])}) "

    # Q: all 
    all_bare_pat = pron_prefix + r"all" + coda
    pattern_regex["q_all_bare"] = re.compile(all_bare_pat, re.IGNORECASE)

    # Q: like 
    like_bare_pat = pron_prefix + r"like" + coda
    pattern_regex["q_like_bare"] = re.compile(like_bare_pat, re.IGNORECASE)

    return pattern_regex

def main():
    # Initialize list of lists
    data = []

    # Initialize regular expressions
    q_form_regex = create_patterns()

    # glob over each text file
    for f in glob("data/*_textfiles_*/*.txt"):
        
        # store filename as speaker code
        speaker_id = os.path.basename(f)
        
        # store region name
        region_id = speaker_id[0:3]
        
        # read over the lines of the file, filtering against interviewer content
        lines = open(f, mode="r").readlines()[1:] # ignore first line with column names

        speaker_lines = [l for l in lines if not INTERVIEWER_RE.match(l)]
        
        # now iterate over each line and check for quotatives before storing
        for line in speaker_lines:
            utt_id, _, _, content, _ = line.split("\t")

            # if there is a quotative form
            for q in q_form_regex.keys():
                form_found = re.search(q_form_regex[q], content)
                if form_found:
                    data.append([
                        speaker_id,
                        content,
                        utt_id,
                        region_id,
                        q, # the quotative type
                        form_found.group() # the target column
                    ])
    
    #### Convert to DataFrame to print brief overview of counts
    df = pd.DataFrame(data, columns=["speaker_id", "utterance", "utt_id", "region_id", "q_type", "target"])
    print(f"Extracted {len(df)} data points")
    print(f"Counts by quotative type:\n\n{df.q_type.value_counts()}")
    
    # create output folder if not exists
    if not os.path.exists("output/"):
        os.mkdir("output/")

    # write data to output
    df.to_csv("output/coraal_q_forms.csv")
    return

if __name__ == "__main__":
    main()