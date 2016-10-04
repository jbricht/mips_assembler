def encode_r_format(funct, rd, rs, rt, opcode=0, shamt=0):
    return (opcode << 26) | (rs << 21) | (rt << 16) | (rd << 11) | (shamt <<
                                                                    6) | funct


def encode_i_format(opcode, rs, rt, immediate):
    return (opcode << 26) | (rs << 21) | (rt << 16) | immediate


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
    'beq': i_format_encoder(0x4),
    'bne': i_format_encoder(0x5),
    'j': j_format_encoder(0x2),
    'jal': j_format_encoder(0x3),
    'jr': lambda rs: encode_r_format(0x8, 0, rs, 0),
    'lbu': i_format_encoder(0x24),
    'lhu': i_format_encoder(0x25),
    'll': i_format_encoder(0x30),
    'lui': lambda rt, immediate: encode_i_format(0xf, 0, rt, immediate),
    'lw': i_format_encoder(0x23),
    'nor': r_format_encoder(0x27),
    'or': r_format_encoder(0x25),
    'ori': i_format_encoder(0xd),
    'slt': r_format_encoder(0x2a),
    'slti': i_format_encoder(0xa),
    'sltia': i_format_encoder(0xb),
    'sltu': r_format_encoder(0x2b),
    'sll': lambda rd, rt, shamt: encode_r_format(0x00, rd, 0, rt, shamt=shamt),
    'srl': lambda rd, rt, shamt: encode_r_format(0x02, rd, 0, rt, shamt=shamt),
    'sb': i_format_encoder(0x28),
    'sc': i_format_encoder(0x38),
    'sh': i_format_encoder(0x29),
    'sw': i_format_encoder(0x2b),
    'sub': r_format_encoder(0x22),
    'subu': r_format_encoder(0x23),
    'div': lambda rs, rt: encode_r_format(0x1a, 0, rs, rt),
    'divu': lambda rs, rt: encode_r_format(0x1b, 0, rs, rt),
    'mfhi': lambda rd: encode_r_format(0x10, rd, 0, 0),
    'mflo': lambda rd: encode_r_format(0x12, rd, 0, 0),
    'mfc0': lambda rd, rs: encode_r_format(0, rd, rs, 0, opcode=0x10),
    'mult': lambda rs, rt: encode_r_format(0x18, 0, rs, rt),
    'multu': lambda rs, rt: encode_r_format(0x19, 0, rs, rt),
    'sra': lambda rd, rt, shamt: encode_r_format(0x3, rd, 0, rt, shamt=shamt)

}

register_names = ['zero', 'at', 'v0', 'v1']
register_names.extend('a{}'.format(i) for i in range(4))
register_names.extend('t{}'.format(i) for i in range(8))
register_names.extend('s{}'.format(i) for i in range(8))
register_names.extend(['t8', 't9', 'k0', 'k1', 'gp', 'sp', 'fp', 'ra'])

registers = dict((name, num) for num, name in enumerate(register_names))
