import struct

import mips_instructions
import parse


class BadLabel(Exception):
    def __init__(self, label):
        self.label = label


class Assembler:
    """
    Tracks symbol values and the current address, keeps a buffer of
    instructions to be assembled.
    """

    def __init__(self):
        self.ip = 0
        self.symbols = dict()
        self.instructions = []

    def def_label(self, label):
        if label in mips_instructions.register_names or label in mips_instructions.encoders.keys():
            raise BadLabel(label)
        else:
            self.symbols['label'] = self.ip

    def push_instruction(self, insn):
        self.instructions.append(insn)
        self.ip += 4

    def encode_operand(self, operand):
        """
        Converts operands from their string representation to their
        numerical representation, resolving label names along the way.
        """

        if parse.decimal_number.match(operand):
            return int(operand)
        elif parse.hex_number.match(operand):
            return int(operand, 16)
        elif operand in mips_instructions.register_names:
            return mips_instructions.registers[operand]
        elif operand in self.symbols:
            return self.symbols[operand]
        else:
            raise ValueError

    def encode_instruction(self, insn):
        encoder = mips_instructions.encoders[insn.mnemonic]
        operands = [self.encode_operand(o) for o in insn.operands]
        instruction_word = encoder(*operands)
        return struct.pack('>I', instruction_word)

    def encode_instructions(self):
        return b''.join(self.encode_instruction(i) for i in self.instructions)

def assemble_file(fp):
    """
    Read in a file and assemble it.
    :param fp: a file-like object containing MIPS assembly code
    :return: a bytes of the assembled machine code.
    """
    assembler = Assembler()
    assembly_statements = parse.parse_file(fp)
    for stmt in assembly_statements:
        if stmt.label:
            assembler.def_label(stmt.label)
        if stmt.instruction:
            assembler.push_instruction(stmt.instruction)
    return assembler.encode_instructions()

