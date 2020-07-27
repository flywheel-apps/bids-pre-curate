import pandas as pd
import argparse


def main(args):
    acq_df = pd.read_csv(args.acquisitions).fillna('')
    sub_df = pd.read_csv(args.subjects).fillna('')
    ses_df = pd.read_csv(args.sessions).fillna('')

    for i, row in acq_df.iterrows():
        acq_df.at[i, 'new_acquisition_label'] = f"{row['existing_acquisition_label']}-renamed-{i}"
        acq_df.at[i, 'modality'] = f'modality-{i}'
        acq_df.at[i, 'task'] = f'task-{i}'
        acq_df.at[i, 'run'] = f'run-{i}'
        acq_df.at[i, 'ignore'] = f'ignore-{i}'

    for i, row in sub_df.iterrows():
        sub_df.at[i, 'new_subject_label'] = args.sub_name

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
