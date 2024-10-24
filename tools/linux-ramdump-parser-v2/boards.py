# Copyright (c) 2014-2019, The Linux Foundation. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 and
# only version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import os

class Board(object):
    """ Class to describe a board the parser knows how to parse
    socid = shared id unique to a board type
    board_num = human readable board number indicating the board type
                (e.g. 8960, 8974)
    cpu = T32 cpu model
    ram_start = start of the DDR
    imem_start = start of location in which the watchdog address is stored
    smem_addr = start of the shared memory region
    phys_offset = physical offset of the board (CONFIG_PHYS_OFFSET)
    wdog_addr = absolute physical address to check for FIQs
    imem_file_name = file name corresponding to imem_start
    kaslr_addr = virtual address relocation offset from vmlinux to ramdump

    It is not recommended to create instances of this class directly.
    Instead, classes should derive from this class and set fiels appropriately
    for each socid

    """
    def __init__(self):
        self.socid = -1
        self.board_num = "-1"
        self.cpu = 'UNKNOWN'
        self.ram_start = 0
        self.imem_start = 0
        self.smem_addr = 0
        self.phys_offset = 0
        self.wdog_addr = 0
        self.imem_file_name = None
        register_board(self)

class BoardKhaje(Board):
    def __init__(self, socid):
        super(BoardKhaje, self).__init__()
        self.socid = socid
        self.board_num = "khaje"
        self.cpu = 'CORTEXA53'
        self.ram_start = 0x40000000
        self.smem_addr = 0x6000000
        self.smem_addr_buildinfo = 0x6007210
        self.phys_offset = 0x40000000
        self.imem_start = 0x0c100000
        self.kaslr_addr = 0x0c1256d0
        self.wdog_addr = 0x0c125658
        self.imem_file_name = 'OCIMEM.BIN'

class BoardParrot(Board):
  def __init__(self, socid):
    super(BoardParrot, self).__init__()
    self.socid = socid
    self.board_num = "parrot"
    self.cpu = 'CORTEXA53'
    self.ram_start = 0x80000000
    self.smem_addr = 0x900000
    self.smem_addr_buildinfo = 0x9071e0
    self.phys_offset = 0xA8000000
    self.imem_start = 0x14680000
    self.kaslr_addr = 0x146aa6d0
    self.wdog_addr = 0x146aa658
    self.imem_offset_memdump_table = 0x2a010
    self.imem_file_name = 'OCIMEM.BIN'
    self.tbi_mask = 0x4000000000
    self.hyp_diag_addr = 0x146AAB30
    self.rm_debug_addr = 0x146AABEC


def register_board(b):
    global boards
    boards.append(b)

def get_supported_boards():
    """ Called by other part of the code to get a list of boards """

    dir = os.path.join(os.path.dirname(__file__), 'extensions', 'board_def.py')
    if os.path.exists(dir):
        import extensions.board_def
    return boards

def get_supported_ids():
    """ Returns a list of ids to be used with --force-hardware"""
    return list(set(b.board_num for b in boards))


boards = list()
boards.append(BoardKhaje(socid=518))
BoardParrot(socid=537)
BoardParrot(socid=613)