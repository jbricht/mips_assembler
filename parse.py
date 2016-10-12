import collections
import re
import enum

import mips_instructions

decimal_number = re.compile('-?[0-9]+')
hex_number = re.compile('-?0x[0-9a-f]+', re.IGNORECASE)
comma = re.compile(',')
AsmInstruction = collections.namedtuple('AsmInstruction', ['mnemonic', 'operands'])
Token = collections.namedtuple("Token", ['type', 'value'])
OperandType = enum.Enum('OperandType', 'label literal register displaced')
AsmStatement = collections.namedtuple('AsmStatement', ['label', 'instruction'])

class ParseError(Exception):
    def __init__(self, pos, expected, gotten):
        self.pos = pos
        self.expected = expected
        self.gotten = gotten


class Lexer:
    punctuation_types = {
        ':': 'colon',
        ',': 'comma',
        '$': 'dollar',
        '\n': 'newline',
        '(': 'left_paren',
        ')': 'right_paren'
    }
    punctuation = ''.join(punctuation_types.keys())
    mnemonics = set(mips_instructions.encoders.keys())
    registers = set(mips_instructions.register_names)
    whitespace = re.compile(r'[ \t]+')
    identifier = re.compile(r'[a-z_][a-z0-9_]*', re.I)
    decimal = re.compile('-?[0-9]+')
    hex = re.compile('-?0x[0-9a-fA-F]+')

    def __init__(self, input_string):
        self.pos = 0
        self.input = input_string
        pass

    def match_re(self, compiled_re):
        return compiled_re.match(self.input, self.pos)

    def next_token(self):
        # match single-character punctuation
        cur = self.input[self.pos]
        if cur in self.punctuation:
            self.pos += 1
            return Token(self.punctuation_types[cur], cur)
        """
        The re package does not have any way to do maximal-munch, so the
        following is necessary to resolve ambiguities between identifiers,
        mnemonics, and registers, as well as ambiguities among mnemonics
        such as add, addi, addiu, etc.
        """
        m = self.match_re(self.identifier)
        if m:
            self.pos = m.end()
            if m.group() in self.mnemonics:
                tok_type = 'mnemonic'
            elif m.group() in self.registers:
                tok_type = 'register'
            else:
                tok_type = 'identifier'
            return Token(tok_type, m.group())
        m = self.match_re(self.whitespace)
        if m:
            self.pos = m.end()
            return Token('whitespace', m.group())
        m = self.match_re(self.decimal)
        if m:
            self.pos = m.end()
            return Token('decimal', m.group())
        m = self.match_re(self.hex)
        if m:
            self.pos = m.end()
            return Token('hex', m.group())
        return None  # No matching token found

    def lex(self):
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
                base_reg = self.register()
                self.match('right_paren')
                return OperandType.displaced, lit, base_reg
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


def unpack_operand_list(ops):
    """
    This massages lists of operands into the order expected by the encoders,
    and unpacks them from Tokens into bare strings.
    """
    if len(ops) > 3:  # no instruction has more than 3 operands
        raise Exception
    if OperandType.displaced in [o[0] for o in ops]:
        # must be of the form op rt, disp(rs)
        if ops[0][0] != OperandType.register or len(ops) != 2:
            raise Exception
        rs = ops[1][2]
        displacement = ops[1][1]
        rt = ops[0][1]
        return rs.value, rt.value, displacement.value
    else:
        return [o[1].value for o in ops]

def none_safe_value(foo):
    # null checks are cool i guess
    if foo is None:
        return None
    else:
        return foo.value

def parse_file(fp):
    """
    Lexes and parses a file line by line.
    :param fp: The assembler source file to parse.
    :return: An iterator of AsmStatements
    """
    for line in fp.readlines():
        if not line or line == '\n':
            continue
        if not line.endswith('\n'):
            line += '\n'
        label, mnemonic, op_list = Parser(Lexer(line).lex()).line()
        if mnemonic is None:
            yield AsmStatement(label.value, None)
        else:
            yield AsmStatement(none_safe_value(label),
                                AsmInstruction(none_safe_value(mnemonic), unpack_operand_list(op_list)))




if __name__ == '__main__':
    from pprint import pprint

    test_file = open('strcpy.asm', 'r')
    parsed_lines = []
    for l in test_file.readlines():
        p = Parser(Lexer(l).lex())
        parsed_lines.append(p.line())
    pprint(parsed_lines)
