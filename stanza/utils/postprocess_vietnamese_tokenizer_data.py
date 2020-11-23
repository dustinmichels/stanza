import argparse
import re
import sys
from collections import Counter
import json

WORDCHAR_RE = re.compile(r'^\w$', flags=re.UNICODE)
NOT_WORDCHAR_RE = re.compile(r'^\W+$', flags=re.UNICODE)
WHITESPACE_RE = re.compile(r'^\s$', flags=re.UNICODE)

def para_to_chunks(text, char_level_pred):
    chunks = []
    preds = []
    lastchunk = ''
    lastpred = ''
    for idx in range(len(text)):
        if WORDCHAR_RE.match(text[idx]):
            lastchunk += text[idx]
        else:
            if len(lastchunk) > 0 and not NOT_WORDCHAR_RE.match(lastchunk):
                chunks += [lastchunk]
                assert len(lastpred) > 0
                preds += [int(lastpred)]
                lastchunk = ''
            if not WHITESPACE_RE.match(text[idx]):
                # punctuation
                # we add lastchunk in case there was leading whitespace
                chunks += [lastchunk + text[idx]]
                lastchunk = ''
                preds += [int(char_level_pred[idx])]
            else:
                # prepend leading white spaces to chunks so we can tell the difference between "2 , 2" and "2,2"
                lastchunk += text[idx]
        lastpred = char_level_pred[idx]

    if len(lastchunk) > 0:
        chunks += [lastchunk]
        preds += [int(lastpred)]

    return list(zip(chunks, preds))

def paras_to_chunks(text, char_level_pred):
    return [para_to_chunks(re.sub(r'\s', ' ', pt.rstrip()), pc) for pt, pc in zip(text.split('\n\n'), char_level_pred.split('\n\n'))]

def main(args):
    parser = argparse.ArgumentParser()

    parser.add_argument('plaintext_file', type=str, help="Plaintext file containing the raw input")
    parser.add_argument('--char_level_pred', type=str, default=None, help="Plaintext file containing character-level predictions")
    parser.add_argument('-o', '--output', default=None, type=str, help="Output file name; output to the console if not specified (the default)")

    args = parser.parse_args(args=args)

    with open(args.plaintext_file, 'r') as f:
        text = ''.join(f.readlines()).rstrip()
        text = '\n\n'.join([x for x in text.split('\n\n')])

    if args.char_level_pred is not None:
        with open(args.char_level_pred, 'r') as f:
            char_level_pred = ''.join(f.readlines())
    else:
        char_level_pred = '\n\n'.join(['0' * len(x) for x in text.split('\n\n')])

    assert len(text) == len(char_level_pred), 'Text has {} characters but there are {} char-level labels!'.format(len(text), len(char_level_pred))

    output = sys.stdout if args.output is None else open(args.output, 'w')

    json.dump(paras_to_chunks(text, char_level_pred), output)

    output.close()

if __name__ == '__main__':
    main(sys.argv[1:])
