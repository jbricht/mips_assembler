import collections
import re

import mips_instructions

mnemonic = re.compile('|'.join(mips_instructions.encoders.keys()),
                      re.IGNORECASE)
label_def = re.compile(r'([a-zA-Z1-9_]+):')
identifier = re.compile(r'[a-z1-9]', re.IGNORECASE)
whitespace = re.compile(r'[ \t]+')
register_operand = re.compile(
    r'\$(' + '|'.join(mips_instructions.register_names) + ')', re.IGNORECASE)
decimal_number = re.compile('[0-9]+')
hex_number = re.compile('0x[0-9a-f]+', re.IGNORECASE)
comma = re.compile(',')
token_rules = [
    ('whitespace', r'[ \t]+'),
    ('colon', ':'),
    ('comma', ','),
    ('dollar', '\\$'),
    ('newline', '\n'),
    ('left_paren', r'\('),
    ('right_paren', r'\)'),
    ('mnemonic', '|'.join(mips_instructions.encoders.keys())),
    ('register', '|'.join(mips_instructions.register_names)),
    ('decimal', '[0-9]+'),
    ('hex', '0x[0-9a-fA-F]+'),
    ('identifier', '[a-zA-Z_][a-zA-Z0-9_]*')
]
Instruction = collections.namedtuple('Instruction', ['mnemonic', 'operands'])
Token = collections.namedtuple("Token", ['type', 'value'])


class ParseError(Exception):
    def __init__(self, pos, expected, gotten):
        self.pos = pos
        self.expected = expected
        self.gotten = gotten


class Lexer:
    def __init__(self, rules):
        self.rules = [(name, re.compile(regex)) for (name, regex) in rules]

    def next_token(self):
        for (token_type, token_re) in self.rules:
            m = token_re.match(self.input, self.pos)
            if m:
                self.pos = m.end()
                return Token(token_type, m.group())
        return None

    def lex(self, input):
        self.pos = 0
        self.input = input

        while self.pos < len(self.input):
            t = self.next_token()
            if t is None:
                raise Exception("Could not find valid token.", self.pos)
            elif t.type == 'whitespace':
                continue
            else:
                yield t


class Parser:
    def __init__(self, tokens):
        self.pos = 0
        self.toks = list(tokens)

    def cur_tok(self):
        return self.toks[self.pos]

    def next_tok(self):
        self.pos += 1
        return self.cur_tok()

    def match_tok(self, tok_type):
        if self.cur_tok().type != tok_type:
            raise ParseError(self.pos, tok_type, self.cur_tok().type)
        return self.cur_tok()

    def expect_tok(self, tok_type):
        self.next_tok()
        return self.match_tok(tok_type)

    def match_label_def(self):
        label = self.match_tok("identifier")
        self.expect_tok("colon")
        return label

    def match_operand(self):
        if self.cur_tok().type in ['decimal', 'hex', 'identifier']:
            return self.cur_tok()
        elif self.cur_tok().type == 'dollar':
            return self.expect_tok('register')
        else:
            raise ParseError(self.pos, None, self.cur_tok().type)

    def parse_line(self):
        if self.cur_tok().type == 'identifier':
            label = self.match_label_def().value
        else:
            label = None

        if self.next_tok().type != 'mnemonic':
            raise ParseError(self.pos, 'mnemonic', self.cur_tok().type)
        else:
            mnemonic = self.cur_tok().value
        operands = []
        while self.next_tok().type in ['dollar', 'register', 'decimal', 'hex', 'identifier']:
            operands.append(self.match_operand())
            if self.next_tok().type != 'comma':
                break
        if self.cur_tok().type != 'newline': raise ParseError(self.pos, 'newline', self.cur_tok().type)
        return (label, mnemonic, operands)
