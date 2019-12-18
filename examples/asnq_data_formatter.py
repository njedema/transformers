import jsonlines
import os
import argparse
import csv
from bs4 import BeautifulSoup


DATA_DIR = '/Users/jedem/Kaggle/data/'
REQUIRED_INPUT_FIELDS = ['example_id', 'question_text', 'document_text', 'long_answer_candidates',]
ASNQ_OUTPUT_FIELDS = ['question', 'answer', 'annotation']


def read_file(file_path: str):
    print('Reading from {}'.format(file_path))
    with jsonlines.open(file_path) as reader:
        for obj in reader:
            missing = []
            for field in REQUIRED_INPUT_FIELDS:
                if field not in obj:
                    missing.append(field)
            if missing:
                print('Skipping line; missing {}'.format(missing))
                continue
            else:
                yield obj


def write_asnq_format(file_path: str, lines):
    """
    :param file_path: Output file path
    :param lines: Generator of lines to write out
    Writes a .tsv file out with one line per candidate in line.clean_candidates
    """
    LINES_LOG_INTERVAL = 5000
    with open(file_path, 'a+') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=ASNQ_OUTPUT_FIELDS, delimiter=" ")  # delimiter is a tab -> .tsv
        for line in enumerate(lines):
            clean_candidates = line[1].get('clean_candidates')
            question = line[1].get('question_text')
            annotation = line[1].get('annotation')
            for candidate in clean_candidates:
                output_line = {'question': question, 'answer': candidate}
                output_line['annotation'] = annotation if annotation else None
                writer.writerow(output_line)
            if line[0] % LINES_LOG_INTERVAL == 0:
                print('Appending {} lines to {}'.format(LINES_LOG_INTERVAL, file_path))


def clean_candidates(lines):
    """
    :param lines: A generator of dictionaries representing rows from the input file
    :return: A generator of the same lines with clean_candidates in place of candidates
    The ASNQ transfer task doesn't use Lowercase and doesn't strip punctuation or numeric. The only cleaning necessary
    is simply to extract the paragraph from the HTML representation of the candidate.
    """
    for line in lines:
        candidates = line.pop('candidates')
        clean = []
        for candidate in candidates:
            soup = BeautifulSoup(candidate['text'], features="html.parser")
            # there may be multiple paragraphs in a candidate; pull out the text and aggregate them into one candidate
            paragraphs = soup.find_all('p')
            clean_candidate = " ".join(sentence.get_text() for sentence in paragraphs)
            if clean_candidate and clean_candidate not in [" ", "   "]:  # space and tab
                clean.append(clean_candidate)
        line['clean_candidates'] = clean
        yield line


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
    lines = read_file(os.path.join(DATA_DIR, kwargs.get('file')))
    candidates = extract_candidate_strings(lines)
    cleaned_lines = clean_candidates(candidates)
    write_asnq_format(kwargs.get('output_file'), cleaned_lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('kaggle_data_formatter')
    parser.add_argument('-f', '--file', type=str, required=True,
                        help='Path of a file to parse into ASNQ format; must live in DATA_DIR {}'.format(DATA_DIR))
    parser.add_argument('--output_file', type=str,
                        help='Path to write the ASNQ formatted file to; must live in DATA_DIR {}'.format(DATA_DIR))
    arg_dict = vars(parser.parse_args())
    if not arg_dict.get('output_file'):
        file_name = arg_dict.get('file').split('/')[-1]
        file_name_no_suffix = file_name.split('.')[0].replace("-", "_")
        _output_file = os.path.join(DATA_DIR, '{}_ansq_formatted.tsv'.format(file_name_no_suffix))
        arg_dict['output_file'] = _output_file

    main(**arg_dict)
