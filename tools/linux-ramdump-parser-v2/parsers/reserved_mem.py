# Copyright (c) 2018-2020,2021 The Linux Foundation. All rights reserved.
# Copyright (c) 2022-2024 Qualcomm Innovation Center, Inc. All rights reserved.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 and
# only version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import os, re
from parser_util import register_parser, RamParser
from print_out import print_out_str
from mm import get_vmemmap, page_buddy
from mm import pfn_to_page, page_buddy, page_count, for_each_pfn
from mm import page_to_pfn, pfn_to_section
from utils.anomalies import Anomaly
from .pagetracking import PageTrace

def print_reserved_mem(ramdump):
    reserved_mem_addr = ramdump.address_of('reserved_mem')
    output_file = ramdump.open_file("reserved_mem.txt")
    reserved_mem_count = ramdump.read_int('reserved_mem_count')
    size_of_reserved_mem = ramdump.sizeof('struct reserved_mem')
    output_file.write("reserved_mem {\n")
    str = "name = 0x{0:x} '{1}'\n\t\tbase = 0x{2:x}\n\t\tsize = 0x{" \
          "3:x} ({4})KB\n\t\trange = <0x{5:x} - 0x{6:x}>\n\t"
    index = 0
    while index < reserved_mem_count:
        reserved_mem = reserved_mem_addr + index*size_of_reserved_mem
        name_addr = ramdump.read_structure_field(
                            reserved_mem, 'struct reserved_mem', 'name')
        name = ramdump.read_cstring(name_addr, 48)
        base = ramdump.read_structure_field(
                            reserved_mem, 'struct reserved_mem', 'base')
        size = ramdump.read_structure_field(
                            reserved_mem, 'struct reserved_mem', 'size')
        output_file.write("\t{\n\t\t")
        output_file.write(str.format(name_addr, name, base, size, size // 1024,
                                     base, base+size))
        output_file.write("}\n")
        index = index + 1
    output_file.write("\n}")
    output_file.close()

def print_tasklet_info(ramdump, core, tasklet):
    tasklet_vec_addr = ramdump.address_of(tasklet)
    tasklet_head = tasklet_vec_addr + ramdump.per_cpu_offset(core)
    tasklet_head = ramdump.read_word(tasklet_head)
    next_offset = ramdump.field_offset('struct tasklet_struct', 'next')
    func_offset = ramdump.field_offset('struct tasklet_struct', 'func')
    count_offset = ramdump.field_offset('struct tasklet_struct', 'count')
    if tasklet_head != 0x0:
        print_out_str("Pending Tasklet info for {0}:".format(tasklet))

    while (tasklet_head != 0x0):
        print_out_str("struct tasklet_struct: 0x{0:x}:".format(tasklet_head))
        tasklet_func_addr = ramdump.read_word(tasklet_head + func_offset)
        tasklet_func = ramdump.unwind_lookup(tasklet_func_addr)
        if tasklet_func is None:
            tasklet_func = "Dynamic module/symbol not found"
        else:
            tasklet_func = tasklet_func[0]
        print_out_str("\tfunc : 0x{:<16x} -> {}".format(tasklet_func_addr, tasklet_func))
        count = ramdump.read_int(tasklet_head + count_offset)
        if count != 0:
            print_out_str("\tcount: 0x{:<16x} -> this tasklet is disabled".format(count))
        else:
            print_out_str("\tcount: 0x{:<16x} -> this tasklet is enabled".format(count))
        tasklet_head = ramdump.read_word(tasklet_head + next_offset)


def parse_softirq_stat(ramdump):
    irq_stat_addr = ramdump.address_of('irq_stat')
    softirq_name_addr = ramdump.address_of('softirq_to_name')
    sizeof_softirq_name = ramdump.sizeof('softirq_to_name')
    sofrirq_name_arr_size = sizeof_softirq_name // ramdump.sizeof('char *')
    no_of_cpus = ramdump.get_num_cpus()
    index = 0
    size_of_irq_stat = ramdump.sizeof('irq_cpustat_t')
    for index in ramdump.iter_cpus():
        if ramdump.kernel_version >= (4, 19):
            irq_stat = irq_stat_addr + ramdump.per_cpu_offset(index)
        else:
            irq_stat = irq_stat_addr + index*size_of_irq_stat
        softirq_pending = ramdump.read_structure_field(
                                irq_stat, 'irq_cpustat_t', '__softirq_pending')
        pending = ""
        pos = sofrirq_name_arr_size - 1
        while pos >= 0:
            if softirq_pending & (1 << pos):
                flag_addr = ramdump.read_word(ramdump.array_index(
                    softirq_name_addr, "char *", pos))
                flag = ramdump.read_cstring(flag_addr, 48)
                pending += flag
                pending += " | "
            pos = pos - 1
        if pending == "":
            pending = "None"
        else:
            pending = pending.rstrip().rstrip("|")
        print_out_str("core {0} : __softirq_pending = {1}".format(
                                index, pending))
        if "TASKLET" in pending or "HI" in pending:
            print_tasklet_info(ramdump, index, 'tasklet_vec')
            print_tasklet_info(ramdump, index, 'tasklet_hi_vec')

def check_qseecom_invalid_cmds(ramdump):
    invalid_qsecom_cmds_id = ["3", "5", "7", "9", "14", "15", "16", "17", "19", "23" , "29"]
    invalid_qsecom_cmds = []
    return_string = ""
    if os.path.exists(os.path.join(ramdump.outdir, "qsee_log.txt")):
        if os.stat(os.path.join(ramdump.outdir, "qsee_log.txt")).st_size:
            with open(os.path.join(ramdump.outdir, "qsee_log.txt"), "r+") as fd:
                for line in fd:
                    if re.search("TZ App cmd handler, cmd_id", line):
                        cmd_id = line.split()[-1]
                        if cmd_id in invalid_qsecom_cmds_id:
                            invalid_qsecom_cmds.append(cmd_id)
            if len(invalid_qsecom_cmds):
                return_string += "qsecomm sample app running invalid cmds : "
                for i in range(len(invalid_qsecom_cmds)):
                    return_string += invalid_qsecom_cmds[i] + " "
                return (return_string + "\n")
    return return_string

def do_parse_qsee_log(ramdump):
    qsee_out = ramdump.open_file('qsee_log.txt')
    g_qsee_log_addr = ramdump.address_of('g_qsee_log')
    g_qsee_log_v2_addr = ramdump.address_of('g_qsee_log_v2')
    tzdbg_addr = ramdump.address_of('tzdbg')
    is_enlarged_buf_addr = ramdump.field_offset('struct tzdbg', 'is_enlarged_buf')
    is_enlarged_buf = False
    if is_enlarged_buf_addr is not None:
        is_enlarged_buf = ramdump.read_bool(tzdbg_addr + is_enlarged_buf_addr)
    log_buf_offset = ramdump.field_offset('struct tzdbg_log_t', 'log_buf')
    qsee_log_buf_size = 0x8000 ##define QSEE_LOG_BUF_SIZE 0x8000
    if is_enlarged_buf is True:
        qsee_log_buf_size = 0x20000 ##define QSEE_LOG_BUF_SIZE_V2 0x20000
        g_qsee_log_addr = g_qsee_log_v2_addr
        log_buf_offset = ramdump.field_offset('struct tzdbg_log_v2_t', 'log_buf')
    if g_qsee_log_addr is None:
        print_out_str("!!! g_qsee_logs not found")
        qsee_out.close()
        return
    try:
        g_qsee_log_addr = ramdump.read_word(g_qsee_log_addr)
    except Exception as e:
        print_out_str('!!! Cannot read g_qsee_log_addr')
        qsee_out.close()
        return
    log_buf_addr = g_qsee_log_addr + log_buf_offset
    qsee_log_data = ramdump.read_cstring(log_buf_addr, qsee_log_buf_size)
    qsee_log_data = qsee_log_data.rstrip(' \t\r\n\0')
    qsee_out.write(qsee_log_data)
    qsee_out.close()


@register_parser('--print-reserved-mem', 'Print reserved memory info ')
class ReservedMem(RamParser):

    def parse(self):
        print_reserved_mem(self.ramdump)


@register_parser('--print-cma-areas', 'Print cma memory region info ')
class CmaAreas(RamParser):
    def __init__(self, *args):
        super(CmaAreas, self).__init__(*args)
        self.offset_comm = self.ramdump.field_offset('struct page_owner', 'comm')
        if self.ramdump.is_config_defined('CONFIG_PAGE_OWNER'):
            self.pagetrace = PageTrace(self.ramdump)

    def parse_pfn(self, ramdump, pfn, cma, op_file, dict):

        vmemmap = get_vmemmap(ramdump)
        page_size = ramdump.sizeof('struct page')
        page = vmemmap + pfn * page_size
        str = "{0} pfn : 0x{1:x} page : 0x{2:x} flag : 0x{3:x} mapping : 0x{" \
              "4:x} count : {5} _mapcount : {6:x}  PID : {7}{8} {9}\n ts_nsec      {10:>32d} \n free_ts_nsec {11:>32d} \n{12}\n"
        str1 = "{0} pfn : 0x{1:x}--0x{2:x} head_page : 0x{3:x} flag : {4:x} " \
               "mapping : 0x{5:x} count : {6} _mapcount : {7:x} {8}\n{9}\n"
        str2 = "{0} pfn : 0x{1:x} pge : 0x{2:x} count : {3} _mapcount : " \
               "{4:x} {5}\n"
        str3 = "{0} pfn : 0x{1:x}--0x{2:x} head_page : 0x{3:x} count : {4} " \
               "_mapcount : {5:x}  {6}\n"
        page_flags = ramdump.read_structure_field(page, 'struct page', 'flags')
        tail_page = ramdump.read_structure_field(
            page, 'struct page', 'compound_head')
        if (tail_page & 1) == 1:
            page = tail_page - 1
        nr_pages = 1
        page_count = ramdump.read_structure_field(
            page, 'struct page', '_refcount.counter')
        mapcount_offset = ramdump.field_offset('struct page', '_mapcount')
        page_mapcount = ramdump.read_int(page + mapcount_offset)

        if page_mapcount == 0xffffffff:
            page_mapcount = -1
        page_mapping = ramdump.read_structure_field(page, 'struct page', 'mapping')
        is_pinned_str = ""
        if (page_mapcount >= 0) and ((page_count - page_mapcount) >= 2):
            is_pinned_str = "<===pinned"
        if cma == 1:
            cma_usage = "[devm]"
        else:
            cma_usage = "[ncma]"
            # test if buddy
            if page_mapcount == 0xffffff80:
                cma_usage = "[budd]"
                nr_pages = ramdump.read_structure_field(
                    page, 'struct page', 'private')
                nr_pages = 1 << nr_pages
            elif page_mapping != 0:
                anon_page = page_mapping & 0x1
                if anon_page != 0:
                    cma_usage = "[anon]"
                else:
                    cma_usage = "[file]"
            else:
                cma_usage = "[unkw]"

        if ramdump.is_config_defined('CONFIG_PAGE_OWNER'):
            if (page_buddy(ramdump, page)) or page_count == 0:
                function_list = ""
                pid = -1
                ts_nsec = -1
                free_ts_nsec = -1
                comm = -1
            else:
                function_list, order, pid, ts_nsec, gfp, comm, ext_flags = self.pagetrace.page_trace(pfn, True)
                free_ts_nsec = 0
                if pid in dict:
                    dict[pid] = dict[pid] + 1
                else:
                    dict[pid] = 1
            if nr_pages == 1:
                op_file.write(str.format(
                    cma_usage, pfn, page, page_flags, page_mapping, page_count,
                    page_mapcount, pid, " comm: {}".format(comm) if self.offset_comm is not None else "", \
                    is_pinned_str, ts_nsec, free_ts_nsec, function_list))
            else:
                op_file.write(str1.format(cma_usage, pfn, pfn + nr_pages - 1,
                                          page, page_flags, page_mapping,
                                          page_count, page_mapcount,
                                          is_pinned_str, function_list))
        else:
            if nr_pages == 1:
                op_file.write(str2.format(cma_usage, pfn, page, page_count,
                                          page_mapcount, is_pinned_str))
            else:
                op_file.write(str3.format(
                    cma_usage, pfn, pfn + nr_pages - 1, page, page_count,
                    page_mapcount, is_pinned_str))
        return nr_pages

    def cma_region_dump(self, ramdump, cma, cma_name):
        base_pfn = ramdump.read_structure_field(
            cma, 'struct cma', 'base_pfn')
        cma_count = ramdump.read_structure_field(
            cma, 'struct cma', 'count')
        bitmap = ramdump.read_structure_field(
            cma, 'struct cma', 'bitmap')
        bitmap_end = bitmap + cma_count // 8
        in_system = 1
        end_pfn = base_pfn + cma_count
        name = "cma_report_" + cma_name + ".txt"
        op_file = ramdump.open_file(name)
        op_file.write("CMA report\n")
        op_file.write(" - name : {0}\n".format(cma_name))
        op_file.write(" - base_pfn\t\t\t: 0x{0:x}\n".format(base_pfn))
        op_file.write(" - end_pfn\t\t\t: 0x{0:x}\n".format(end_pfn))
        op_file.write(" - count\t\t\t: 0x{0:x}\n".format(cma_count))
        op_file.write(" - size\t\t\t\t: {0}KB\n".format(cma_count << 0x2))
        op_file.write(" - bitmap_start\t\t: 0x{0:x}\n".format(bitmap))
        op_file.write(" - bitmap_end\t\t: 0x{0:x}\n".format(bitmap_end))
        op_file.write(" - in_system\t\t: {0}\n\n".format(in_system))
        dict = {}
        byte_index = 0
        PFNS_PER_BYTE = 8
        COUNT_TO_BYTE = cma_count // PFNS_PER_BYTE
        list = []
        while byte_index < COUNT_TO_BYTE:
            value = ramdump.read_byte(bitmap + byte_index)
            list.append([bitmap + byte_index, value])
            pfn_index = 0
            while pfn_index < PFNS_PER_BYTE:
                pfn = base_pfn + byte_index * PFNS_PER_BYTE + pfn_index
                bit_value = (value >> pfn_index) & 0x1
                cma = 0
                if bit_value != 0:
                    cma = 1
                else:
                    cma = 0
                if cma == 1:
                    self.parse_pfn(ramdump, pfn, cma, op_file, dict)
                pfn_index = pfn_index + 1
            byte_index = byte_index + 1

        sort_list = sorted(dict.items(), key=lambda kv: kv[1], reverse=True)
        for k, v in sort_list:
            print("PID %-8d alloc times %-8d" % (k, v), file=op_file)
        line_break = 0
        print("bitmap: " % (), file=op_file)
        for item in list:
            print("%02x" % (item[1]), file=op_file, end="")
            line_break = line_break + 1
            if line_break == 16:
                print("%s" % (" "), file=op_file)
                line_break = 0
        op_file.close()

    def print_cma_areas(self, ramdump):
        output_file = ramdump.open_file("cma_report_simple.txt")
        cma_area_count = ramdump.read_u32('cma_area_count')
        cma_area_base_addr = ramdump.address_of('cma_areas')
        cma_index = 0
        size_of_cma_area = ramdump.sizeof('struct cma')
        str = "cma : 0x{0:x} cma_base_pfn : 0x{1:x} size : 0x{2:x} pages ({3}KB)\n"
        str1 = "name : {0}\n\n"
        cma = [0] * cma_area_count
        cma_name = [None] * cma_area_count
        while cma_index < cma_area_count:
            cma_area = cma_area_base_addr + cma_index * size_of_cma_area
            base_pfn = ramdump.read_structure_field(
                cma_area, 'struct cma', 'base_pfn')
            cma_size = ramdump.read_structure_field(
                cma_area, 'struct cma', 'count')
            if (ramdump.kernel_version >= (5, 10, 0)):
                name_addr_offset = ramdump.field_offset('struct cma', 'name')
                name_addr = (cma_area + name_addr_offset)
                name = ramdump.read_cstring(name_addr, 64)
            else:
                name_addr = ramdump.read_structure_field(cma_area, 'struct cma', 'name')
                name = ramdump.read_cstring(name_addr, 48)
            if name == "linux,cma":
                name = "dma_contiguous_default_area"
            cma[cma_index] = cma_area
            cma_name[cma_index] = name
            output_file.write(str.format(cma_area, base_pfn, cma_size, cma_size * 4))
            output_file.write(str1.format(name))
            cma_index = cma_index + 1

        output_file.close()

        cma_index = 0
        while cma_index < cma_area_count:
            cma1 = cma[cma_index]
            cma_name1 = cma_name[cma_index]
            self.cma_region_dump(ramdump, cma1, cma_name1)
            cma_index = cma_index + 1
    def parse(self):
        if self.ramdump.kernel_version < (4, 9):
            print_out_str("Linux version lower than 4.9 is not supported!!")
            return
        else:
            self.print_cma_areas(self.ramdump)


@register_parser('--print-softirq-stat', 'Print softirq pending info ')
class SoftirqStat(RamParser):

    def parse(self):
        parse_softirq_stat(self.ramdump)


@register_parser('--print-qsee-log', 'Extract qsee com logs')
class ParseQseeLog(RamParser):
    def parse(self):
        do_parse_qsee_log(self.ramdump)
        anomaly = Anomaly()
        anomaly.setOutputDir(self.ramdump.outdir)
        return_string = check_qseecom_invalid_cmds(self.ramdump)
        if len(return_string):
            anomaly.addWarning("HLOS", "qsee_log.txt", "{0}".format(return_string))
