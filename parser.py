import collections
import re
import enum

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
OperandType = enum.Enum('OperandType', 'label literal register displaced')


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

    def lex(self, input_string):
        self.pos = 0
        self.input = input_string

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

    def advance_tok(self):
        self.pos += 1

    def match(self, tok_type):
        ct = self.cur_tok()
        if ct.type == tok_type:
            self.advance_tok()
            return ct
        else:
            raise ParseError(self.pos, tok_type, ct.type)

    def register(self):
        self.match("dollar")
        return self.match("register")

    def label(self):
        return self.match("identifier")

    def literal(self):
        # this is ugly, should have one token type for all literals
        ct = self.cur_tok()
        if ct.type in {'hex', 'decimal'}:
            self.advance_tok()
            return ct
        else:
            # eeeew
            raise ParseError(self.pos, "hex or decimal", ct.type)

    def operand(self):
        """
        returns a tuple of the operand type, and the operand itself.
        for disp($reg) operands, returns (type, displacement, register)
        otherwise just (type, operand)
        the displacement must be a literal
        """
        if self.cur_tok().type in {'hex', 'decimal'}:
            # either just a literal or disp($reg)
            lit = self.literal()
            if self.cur_tok().type == 'left_paren':
                self.match('left_paren')
                displaced_reg = self.register()
                self.match('right_paren')
                return OperandType.displaced, lit, displaced_reg
            else:
                return OperandType.literal, lit

        elif self.cur_tok().type == 'identifier':
            return OperandType.label, self.label()
        elif self.cur_tok().type == 'dollar':
            return OperandType.register, self.register()

    def operand_list(self):
        """
        operand {comma operand}
        """
        ops = [self.operand()]

        while self.cur_tok().type == 'comma':
            self.match('comma')
            ops.append(self.operand())
        return ops

    def line(self):
        """
        [identifier colon] [mnemonic [operand_list]] newline
        """
        label = None
        if self.cur_tok().type == "identifier":
            label = self.match("identifier")
            self.match("colon")

        if self.cur_tok().type == 'newline':
            return label, None, None

        mnemo = self.match('mnemonic')

        if self.cur_tok().type == "newline":
            operands = []
        else:
            operands = self.operand_list()

        self.match("newline")
        return label, mnemo, operands


if __name__ == '__main__':
    from sys import stdin

    l = Lexer(token_rules)
    while True:
        input_line = stdin.readline()
        p = Parser(l.lex(input_line))
        print(p.line())
