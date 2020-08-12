import argparse
import re
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parents[2].resolve()))
import pandas as pd
from utils.fly.make_file_name_safe import make_file_name_safe
from numpy.random import randint


def main(args):
    acq_df = pd.read_csv(args.acquisitions).fillna('')
    sub_df = pd.read_csv(args.subjects).fillna('')
    ses_df = pd.read_csv(args.sessions).fillna('')

    # Generate random binary for rows in acquisition df
    # Randomly, or intermittently populate values
    randoms = randint(2, size=acq_df.shape[0])
    for i, row in acq_df.iterrows():
        acq_df.at[i, 'new_acquisition_label'] =  \
            f"{make_file_name_safe(row['existing_acquisition_label'], re.compile('[^A-Za-z0-9]'), '')}"

        acq_df.at[i, 'modality'] = (f'T1{i}'
                                    if not randoms[i] else '')
        acq_df.at[i, 'task'] = (f'task{i}'
                                if i % 3 == 0 else '')
        acq_df.at[i, 'run'] = (f'{i}'
                               if i % 4 == 0 else '')
        acq_df.at[i, 'ignore'] = ('yes'
                                  if i % 5 == 0 else '')

    for i, row in sub_df.iterrows():
        sub_df.at[i, 'new_subject_label'] = (args.sub_name
                                             if i != 0 else '')

    # don't populate first row to test blank column
    for i, row in ses_df.iterrows():
        ses_df.at[i, 'new_session_label'] = f"{row['existing_session_label']}_{i}"

    acq_df.to_csv(args.acquisitions, index=False, index_label=False)
    ses_df.to_csv(args.sessions, index=False, index_label=False)
    sub_df.to_csv(args.subjects, index=False, index_label=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--acquisitions')
    parser.add_argument('--sessions')
    parser.add_argument('--subjects')
    parser.add_argument('--sub-name')

    args = parser.parse_args()

    main(args)
