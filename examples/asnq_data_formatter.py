import jsonlines
import os
import argparse


DATA_DIR = '/Users/jedem/Kaggle/data/'
REQUIRED_FIELDS = ['example_id',
                   'question_text',
                   'document_text',
                   'long_answer_candidates',
                   ]


def read_file(file_path: str):
    print('Reading from {}'.format(file_path))
    with jsonlines.open(file_path) as reader:
        for obj in reader:
            missing = []
            for field in REQUIRED_FIELDS:
                if field not in obj:
                    missing.append(field)
            if missing:
                print('Skipping line; missing {}'.format(missing))
                continue
            else:
                yield obj


def write_asnq_format(file_path: str, lines):
    pass


def clean_lines(lines):
    return []


def extract_candidate_strings(lines):
    for line in lines:
        document = line.get('document_text').split()
        candidates = line.pop('long_answer_candidates')
        output_candidates = []
        for candidate_offsets in candidates:
            start = candidate_offsets.get('start_token')
            stop = candidate_offsets.get('end_token')
            candidate_offsets['text'] = " ".join(document[start: stop])
            output_candidates.append(candidate_offsets)
        line['candidates'] = output_candidates
        yield line


def main(**kwargs):
    lines = read_file(kwargs.get('file'))
    candidates = extract_candidate_strings(lines)
    for line in candidates:
        print(line.get('candidates'))
    #cleaned_candidates = clean_lines(candidates)
    #write_asnq_format(kwargs.get('output_file'), cleaned_candidates)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('kaggle_data_formatter')
    parser.add_argument('-f', '--file', type=str,
                        help='Path of a file to parse into ASNQ format')
    parser.add_argument('--output_file', type=str,
                        help='Path to write the ASNQ formatted file to')
    arg_dict = vars(parser.parse_args())
    if not arg_dict.get('output_file'):
        file_name = arg_dict.get('file').split('/')[-1]
        file_name_no_suffix = file_name.split('.')[-1]
        _output_file = os.path.join(DATA_DIR, '{}_ansq_formatted.tsv'.format(file_name_no_suffix))
        arg_dict['output_file'] = _output_file

    main(**arg_dict)
