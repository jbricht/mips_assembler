def encode_r_format(funct, rd, rs, rt, opcode=0, shamt=0):
    return (opcode << 26) | (rs << 21) | (rt << 16) | (rd << 11) | (shamt <<
                                                                    6) | funct


def encode_i_format(opcode, rs, rt, immediate):
    return (opcode << 26) | (rs << 21) | (rt << 16) | (immediate & 0xffff)


def encode_j_format(opcode, address):
    return (opcode << 26) | address


def r_format_encoder(funct):
    """
    returns an encoder for the most common r-format instructions, which operate
    on three registers rd rs rt, take no shamt, and have opcode 0
    """

    def encoder(rd, rs, rt):
        return encode_r_format(funct, rd, rs, rt)

    return encoder


def i_format_encoder(opcode):
    """
    returns an encoder fror the most common i-format instructions, which use
    rt, rs, and an immediate
    """

    def encoder(rt, rs, immediate):
        return encode_i_format(opcode, rs, rt, immediate)

    return encoder


def j_format_encoder(opcode):
    def encoder(address):
        return encode_j_format(opcode, address)

    return encoder


# map mnemonics to functions which encode that instruction
encoders = {
    'add': r_format_encoder(0x20),
    'addi': i_format_encoder(0x8),
    'addiu': i_format_encoder(0x9),
    'addu': r_format_encoder(0x21),
    'and': r_format_encoder(0x24),
    'andi': i_format_encoder(0xc),
    'b': lambda offset: 0b000100 << 26 | offset,
    'bal': lambda offset: 0b000001 << 26 | 0b10001 << 16 | offset,
    'beq': i_format_encoder(0x4),
    'bgez': lambda rs,
                   offset: 0b000001 << 26 | rs << 21 | 0b00001 << 16 | offset,
    'bgezal': lambda rs,
                     offset: 0b000001 << 26 | rs << 21 | 0b10001 << 16 | offset,
    'bgtz': lambda rs, offset: 0b000111 << 26 | rs << 21 | offset,
    'blez': lambda rs, offset: 0b000110 << 26 | rs << 21 | offset,
    'bltz': lambda rs, offset: 0b000001 << 26 | rs << 21 | offset,
    'bltzal': lambda rs,
                     offset: 0b000001 << 26 | rs << 21 | 0b10000 << 16 | offset,
    'bne': i_format_encoder(0x5),
    'break': lambda code: code << 6 | 0b001101,
    'div': lambda rs, rt: encode_r_format(0x1a, 0, rs, rt),
    'divu': lambda rs, rt: encode_r_format(0x1b, 0, rs, rt),
    'j': j_format_encoder(0x2),
    'jal': j_format_encoder(0x3),
    'jalr': lambda rd, rs: rs << 21 | rd << 11 | 0b001001,
    'jr': lambda rs: encode_r_format(0x8, 0, rs, 0),
    'lb': i_format_encoder(0b100000),
    'lbu': i_format_encoder(0x24),
    'lh': i_format_encoder(0b100001),
    'lhu': i_format_encoder(0x25),
    'lui': lambda rt, immediate: encode_i_format(0xf, 0, rt, immediate),
    'lw': i_format_encoder(0x23),
    'lwl': i_format_encoder(0b100010),
    'lwr': i_format_encoder(0b100110),
    'mfhi': lambda rd: encode_r_format(0x10, rd, 0, 0),
    'mflo': lambda rd: encode_r_format(0x12, rd, 0, 0),
    'mthi': lambda rs: rs << 21 | 0b010001,
    'mtlo': lambda rs: rs << 21 | 0b010011,
    'mult': lambda rs, rt: encode_r_format(0x18, 0, rs, rt),
    'multu': lambda rs, rt: encode_r_format(0x19, 0, rs, rt),
    'nop': lambda: 0,
    'nor': r_format_encoder(0x27),
    'or': r_format_encoder(0x25),
    'ori': i_format_encoder(0xd),
    'sb': i_format_encoder(0x28),
    'sh': i_format_encoder(0x29),
    'sll': lambda rd, rt, shamt: encode_r_format(0x00, rd, 0, rt, shamt=shamt),
    'sllv': lambda rd, rt, rs: encode_r_format(0b000100, rd, rs, rt),
    'slt': r_format_encoder(0x2a),
    'slti': i_format_encoder(0xa),
    'sltiu': i_format_encoder(0xb),
    'sltu': r_format_encoder(0x2b),
    'sra': lambda rd, rt, shamt: encode_r_format(0x3, rd, 0, rt, shamt=shamt),
    'srav': lambda rd, rt, rs: encode_r_format(0b000111, rd, rs, rt),
    'srl': lambda rd, rt, shamt: encode_r_format(0x02, rd, 0, rt, shamt=shamt),
    'srlv': lambda rd, rt, rs: encode_r_format(0b000110, rd, rs, rt),
    'sub': r_format_encoder(0x22),
    'subu': r_format_encoder(0x23),
    'sw': i_format_encoder(0x2b),
    'swl': i_format_encoder(0b101010),
    'swr': i_format_encoder(0b101110),
    'syscall': lambda code: code << 6 | 0b001100,
    'xor': r_format_encoder(0b100110),
    'xori': i_format_encoder(0b001110)
}

register_names = ['zero', 'at', 'v0', 'v1']
register_names.extend('a{}'.format(i) for i in range(4))
register_names.extend('t{}'.format(i) for i in range(8))
register_names.extend('s{}'.format(i) for i in range(8))
register_names.extend(['t8', 't9', 'k0', 'k1', 'gp', 'sp', 'fp', 'ra'])

registers = dict((name, num) for num, name in enumerate(register_names))
