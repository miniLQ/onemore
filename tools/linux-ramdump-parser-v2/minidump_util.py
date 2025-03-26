# Copyright (c) 2012-2017, 2020 The Linux Foundation. All rights reserved.
# Copyright (c) 2022-2024 Qualcomm Innovation Center, Inc. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 and
# only version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import sys
import re
import os
import struct
from print_out import print_out_str
from fnmatch import fnmatch


def minidump_virt_to_phys(ebi_files,addr):
    if addr is None:
        return None

    pa_addr = None
    for a in ebi_files:
        idx, pa, end_addr, va,size = a
        if addr >= va and addr <= va +  size:
            offset = addr - va
            pa_addr = pa + offset
            return pa_addr
    return pa_addr

def read_physical_minidump(ebi_files,ebi_files_ramfile,elffile,addr,length):
    ebi = [-1, -1, -1, -1, -1]
    for a in ebi_files:
        idx, start, end, va, size = a
        if addr >= start and addr <= end:
            ebi = a
            break
    if ebi[0] != -1:
        idx = ebi[0]
        textSec = elffile.get_segment(idx)
        off = addr - ebi[1]
        endoff = off + length
        if endoff > ebi[4]:
            endoff = ebi[4]
        textSec.stream.seek(textSec['p_offset'] + off)
        return textSec.stream.read(endoff - off)
    else:
        ebi = (-1, -1, -1)
        for a in ebi_files_ramfile:
            fd, start, end, path = a
            if addr >= start and addr <= end:
                ebi = a
                break
        if ebi[0] == -1:
            return None
        offset = addr - ebi[1]
        ebi[0].seek(offset)
        a = ebi[0].read(length)
        return a

def add_file(fo, outdir, path):
        try:
            path = os.path.join(outdir, path)
            fi = open(path, "rb")
        except:
            print_out_str("Not able to open file %s" % (path))
            return -1
        while True:
            buf = fi.read(4096)
            if len(buf) == 0:
                break
            fo.write(buf)
        fi.close()
        return 0

def get_strings(buf, length):
        offset = 0
        string = ""
        nlist = []
        begin = False
        str_tbl = ""
        while offset < length:
            str_tbl = ""
            if not begin:
                (ch,) = struct.unpack_from("<B", buf, offset)
                str_tbl += chr(ch)
                (ch,) = struct.unpack_from("<B", buf, offset+1)
                str_tbl += chr(ch)
                (ch,) = struct.unpack_from("<B", buf, offset+2)
                str_tbl += chr(ch)
                (ch,) = struct.unpack_from("<B", buf, offset+3)
                str_tbl += chr(ch)
                (ch,) = struct.unpack_from("<B", buf, offset+4)
                str_tbl += chr(ch)
                (ch,) = struct.unpack_from("<B", buf, offset+5)
                str_tbl += chr(ch)
                (ch,) = struct.unpack_from("<B", buf, offset+6)
                str_tbl += chr(ch)
                if str_tbl == "STR_TBL":
                    begin = True
                    offset += 6
                else:
                    offset += 1
                continue
            (ch,) = struct.unpack_from("<B", buf, offset)
            offset += 1
            if ch >= 0x30 and ch < 0x80:
                string += chr(ch)
            elif (string != "" and len(string) >= 3 and
                  string != 'linux_banner' and string != 'minidump_table'):
                nlist.append(string)
                string = ""
            else:
                string = ""
            if ch == 0:
                (ch1,) = struct.unpack_from("<B", buf, offset+1)
                if ch1 == 0:
                    (ch2,) = struct.unpack_from("<B", buf, offset+2)
                    if ch2 == 0:
                        return nlist
        return nlist

def generate_elf(autodump, outdir, vm, kernel_version):
        if "autogvm" in vm or "autoghgvm" in vm:
            if kernel_version >= (5, 15, 0):
                vmid = str(vm.split("-")[-1]) + "_"
            else:
                vmid = ""
        elif vm == "oemvm":
            vmid = "31_"
        elif vm:
            vmid = "2d_"
        else:
            vmid = ""
        elfhd_old = os.path.join(autodump, "md_" + vmid + "KELF_HEADER.BIN")
        elfhd_new = os.path.join(autodump, "md_" + vmid + "KELF_HDR.BIN")
        if os.path.exists(elfhd_old):
            elfhd = elfhd_old
            fi = open(elfhd, "rb")
        elif os.path.exists(elfhd_new):
            elfhd = elfhd_new
            fi = open(elfhd, "rb")
        else:
            print_out_str("ELF header binary is missing")
            return 1

        outfile = os.path.join(outdir, "ap_minidump.elf")
        fo = open(outfile, "wb")

        hsize = os.path.getsize(elfhd)
        print_out_str("ELF header size %d" % hsize)
        buf = fi.read(hsize)
        fo.write(buf)
        nlist = get_strings(buf, len(buf))
        files = os.listdir(autodump)
        for names in nlist:
            if vm:
                for file in files:
                    if "autogvm" in vm or "autoghgvm" in vm:
                        if re.match(r'^[0-9]_', names) is None:
                            filepath = "md_" + vmid + names + ".BIN"
                            is_found = fnmatch(file, "md_" + vmid + names + "*.BIN")
                        else:
                            filepath = "md_" + names + ".BIN"
                            is_found = fnmatch(file, "md_" + names + "*.BIN")
                    else:
                        filepath = "md_" + vmid + names + ".BIN"
                        is_found = fnmatch(file, "md_" + vmid + names + "*.BIN")
                    if is_found:
                        break;
                if not is_found:
                    return 1
                ret = add_file(fo, autodump, file)
            else:
                filepath = "md_" + names + ".BIN"
                ret = add_file(fo, autodump, filepath)

            if ret == -1:
                fo.close()
                fi.close()
                return 1
        fi.close()
        fo.close()
        return 0
