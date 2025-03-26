# Copyright (c) 2019-2021, The Linux Foundation. All rights reserved.
# Copyright (c) 2022-2025, Qualcomm Innovation Center, Inc. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 and
# only version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from parser_util import register_parser, RamParser
from print_out import print_out_str
from utils.anomalies import Anomaly
import print_out
import os

DEFAULT_MIGRATION_NR=32
DEFAULT_MIGRATION_COST=500000
DEFAULT_RT_PERIOD=1000000
DEFAULT_RT_RUNTIME=950000
SCHED_CAPACITY_SHIFT=10
SCHED_CAPACITY_SCALE=1024

cpu_online_bits = 0

def mask_bitset_pos(cpumask):
    obj = [i for i in range(cpumask.bit_length()) if cpumask & (1<<i)]
    if len(obj) == 0:
        return None
    else:
        return obj

def cpu_isolation_mask(ramdump):
    cpu_isolated_bits = 0
    if (ramdump.kernel_version >= (5, 15, 0)):
        cpu_isolated_bits = ramdump.read_word('__cpu_halt_mask')
    elif (ramdump.kernel_version >= (5, 10, 0)):
        #Isolation replaced with pause feature.
        cpuhp_state_addr = ramdump.address_of('cpuhp_state')
        pause_state = ramdump.gdbmi.get_value_of('CPUHP_AP_ACTIVE') - 1

        for i in ramdump.iter_cpus():
            cpu_state_off = cpuhp_state_addr + ramdump.per_cpu_offset(i)
            state = ramdump.read_structure_field(cpu_state_off, 'struct cpuhp_cpu_state', 'state')
            target = ramdump.read_structure_field(cpu_state_off, 'struct cpuhp_cpu_state', 'target')

            if state == pause_state and target == pause_state:
                cpu_isolated_bits |= 1 << i

    elif (ramdump.kernel_version >= (4, 9, 0)):
        cpu_isolated_bits = ramdump.read_word('__cpu_isolated_mask')
    elif (ramdump.kernel_version >= (4, 4, 0)):
        cpu_isolated_bits = ramdump.read_word('cpu_isolated_bits')
    if cpu_isolated_bits == None:
        cpu_isolated_bits = 0
    return cpu_isolated_bits


def verify_active_cpus(ramdump):
    cpu_topology_addr = ramdump.address_of('cpu_topology')
    cpu_topology_size = ramdump.sizeof('struct cpu_topology')
    cpu_isolated_bits = 0
    global cpu_online_bits

    if (ramdump.kernel_version >= (4, 19, 0)):
        cluster_id_off = ramdump.field_offset('struct cpu_topology', 'package_id')
    else:
        cluster_id_off = ramdump.field_offset('struct cpu_topology', 'cluster_id')

    nr_cpus = ramdump.get_num_cpus()

    # Skip !SMP/UP systems(with single cpu).
    if not ramdump.is_config_defined('CONFIG_SMP') or (nr_cpus <= 1):
        print ("Ramdmp is UP or !SMP or nrcpus <=1 ")
        return

    # Get online cpus from runqueue
    runqueues_addr = ramdump.address_of('runqueues')
    online_offset = ramdump.field_offset('struct rq', 'online')

    for i in ramdump.iter_cpus():
        online = ramdump.read_int(runqueues_addr + online_offset, cpu=i)
        cpu_online_bits |= (online << i)

    if (cluster_id_off is None):
        print_out_str("\n Invalid cluster topology detected\n")

    cpu_isolated_bits = cpu_isolation_mask(ramdump)

    # INFO: from 4.19 onwards, core_sibling mask contains only online cpus,
    #       find out cluster cpus dynamically.

    cluster_cpus = [0]
    for j in ramdump.iter_cpus():
        c_id = ramdump.read_int(cpu_topology_addr + (j * cpu_topology_size) + cluster_id_off)
        if len(cluster_cpus) <= c_id :
            cluster_cpus.extend([0])
        cluster_cpus[c_id] |= (1 << j)

    cluster_data_off = ramdump.address_of('cluster_state')

    for i in range(0, len(cluster_cpus)):
        cluster_online_cpus = cpu_online_bits & cluster_cpus[i]
        cluster_nr_oncpus = bin(cluster_online_cpus).count('1')
        cluster_isolated_cpus = cpu_isolated_bits & cluster_cpus[i]
        cluster_nr_isocpus = bin(cluster_isolated_cpus).count('1')
        crctl_nr_isol = 0

        if cluster_data_off:
        # Get core_ctl isolated cpus:
            clust_addr = ramdump.array_index(cluster_data_off, 'struct cluster_data', i)

            if (ramdump.kernel_version >= (5, 10, 0)):
                crctl_nr_isol = ramdump.read_structure_field(clust_addr, 'struct cluster_data', 'nr_paused_cpus')
            if (ramdump.kernel_version >= (4, 4, 0)):
                crctl_nr_isol = ramdump.read_structure_field(clust_addr, 'struct cluster_data', 'nr_isolated_cpus')

        if (bin(cluster_cpus[i]).count('1') > 2):
            min_req_cpus = 2
        else:
            min_req_cpus = 1

        if ((cluster_nr_oncpus - cluster_nr_isocpus) < min_req_cpus):
                print_out_str("\n" + "*" * 10 + " WARNING " + "*" * 10 + "\n")
                print_out_str("\tMinimum active cpus are not available in the cluster {0}\n".format(i))

                print_out_str("*" * 10 + " WARNING " + "*" * 10 + "\n")
        print_out_str("\tCluster nr_cpu: {0} cpus: {1}  Online cpus: {2} Isolated cpus: {3} (core_ctl nr_isol: {4})\n".format(
                        bin(cluster_cpus[i]).count('1'),
                        mask_bitset_pos(cluster_cpus[i]),
                        mask_bitset_pos(cluster_online_cpus),
                        mask_bitset_pos(cluster_isolated_cpus), crctl_nr_isol))

def dump_rq_lock_information(ramdump):
    runqueues_addr = ramdump.address_of('runqueues')
    if (ramdump.kernel_version >= (5, 15, 0)):
        lock_owner_cpu_offset = ramdump.field_offset('struct rq', '__lock.owner_cpu')
    else:
        lock_owner_cpu_offset = ramdump.field_offset('struct rq', 'lock.owner_cpu')
    if lock_owner_cpu_offset:
        for i in ramdump.iter_cpus():
            lock_owner_cpu = ramdump.read_int(runqueues_addr + lock_owner_cpu_offset, cpu=i)
            print_out_str("\n cpu {0} ->rq_lock owner cpu {1}".format(i, hex(lock_owner_cpu)))
        print_out_str("\n ")

def dump_isolation_data(ramdump):
    try:
        if ramdump.address_of('cluster_state') is not None:
            print_out_str("cluster_state:")
            cluster_state = ramdump.read_datatype('cluster_state')
            for idx in range(0, len(cluster_state)):
                print_out_str("\tcluster{}: min_cpus = {} max_cpus = {} enable = {}".format(
                    idx, cluster_state[idx].min_cpus, cluster_state[idx].max_cpus,
                    cluster_state[idx].enable))
        halt_state_ptr = ramdump.address_of('halt_state')
        if halt_state_ptr is not None:
            print_out_str("\nhalt_state:")
            for cpu in ramdump.iter_cpus():
                halt_state = ramdump.read_u16(halt_state_ptr, cpu=cpu)
                print_out_str("\tcpu{}: client_vote_mask = ({}, {})".format(
                    cpu, halt_state & 0xFF, (halt_state>>8) & 0xFF))
    except Exception as err:
        print_out_str("{}\n".format(str(err)))
        pass
    try:
        cpus_paused_by_us = ramdump.read_word('cpus_paused_by_us')
        cpus_in_max_cooling_level = ramdump.read_word('cpus_in_max_cooling_level')
        the_hcd = ramdump.read_word('the_hcd')
        our_paused_cpus = ramdump.read_structure_field(the_hcd, 'struct hyp_core_ctl_data', 'our_paused_cpus.bits')
        print_out_str("hyp_core_ctl_data->our_paused_cpus: {0:08b}".format(our_paused_cpus))
        if our_paused_cpus == 0x60:
            print_out_str('cpus 5 and 6 are isolated because Secondary VM is running)\n')
        print_out_str("core isolated by thermal: {0:08b}".format(cpus_in_max_cooling_level))
        if cpus_in_max_cooling_level == 0x0:
            print_out_str("thermal has not isolated any cpus\n")
        print_out_str("core_ctl cpus_paused_by_us: {0:08b}".format(cpus_paused_by_us))
        if cpus_paused_by_us == 0x0:
            print_out_str("core_ctl realizes that there is load in the system and hence has asked to UNisolate all the cpus\n")
    except Exception as err:
        pass

def dump_cpufreq_data(ramdump):
    cpufreq_data_addr = ramdump.address_of('cpufreq_cpu_data')
    cpuinfo_off = ramdump.field_offset('struct cpufreq_policy', 'cpuinfo')
    runqueues_addr = ramdump.address_of('runqueues')
    print_out_str("\nCPU Frequency information:\n" + "-" * 10)
    for i in ramdump.iter_cpus():
        cpu_data_addr = ramdump.read_u64(cpufreq_data_addr, cpu=i)
        rq_addr = runqueues_addr + ramdump.per_cpu_offset(i)

        cur_freq = ramdump.read_structure_field(cpu_data_addr, 'struct cpufreq_policy', 'cur')
        min_freq = ramdump.read_structure_field(cpu_data_addr, 'struct cpufreq_policy', 'min')
        max_freq = ramdump.read_structure_field(cpu_data_addr, 'struct cpufreq_policy', 'max')
        freq_table = ramdump.read_structure_field(cpu_data_addr, 'struct cpufreq_policy', 'freq_table')
        cpuinfo_min_freq = ramdump.read_int(cpu_data_addr + cpuinfo_off + ramdump.field_offset('struct cpufreq_cpuinfo', 'min_freq'))
        cpuinfo_max_freq = ramdump.read_int(cpu_data_addr + cpuinfo_off + ramdump.field_offset('struct cpufreq_cpuinfo', 'max_freq'))

        gov = ramdump.read_structure_field(cpu_data_addr, 'struct cpufreq_policy', 'governor')
        gov_name = ramdump.read_cstring(gov + ramdump.field_offset('struct cpufreq_governor', 'name'))

        curr_cap = ramdump.read_structure_field(rq_addr, 'struct rq', 'cpu_capacity')
        # thermal_pressure is architecture(ARM/ARM64) and kconfig(CONFIG_ARM_CPU_TOPOLOGY) related
        if (ramdump.kernel_version >= (5, 10, 0)):
            try:
                max_thermal_cap = (1 << SCHED_CAPACITY_SHIFT)
                thermal_pressure = ramdump.read_u64(ramdump.address_of('thermal_pressure') + ramdump.per_cpu_offset(i))
                thermal_cap = max_thermal_cap - thermal_pressure
            except Exception as err:
                print(err)
        else:
            try:
                thermal_cap = ramdump.read_word(ramdump.array_index(ramdump.address_of('thermal_cap_cpu'), 'unsigned long', i))
            except Exception as err:
                print(err)

        print_out_str("CPU:{0}\tGovernor:{1}\t cur_freq:{2}, max_freq:{3}, min_freq{4}  cpuinfo: min_freq:{5}, max_freq:{6}"
                    .format(i, gov_name, cur_freq, max_freq, min_freq, cpuinfo_min_freq, cpuinfo_max_freq))
                #print_out_str('v.v ((struct cpufreq_frequency_table*)0x{0:x})[0..10]'.format(freq_table))
        try:
            for j in range(0, 30):
                freq_table_index = ramdump.array_index(freq_table, 'struct cpufreq_frequency_table', j)
                frequency = ramdump.read_structure_field(freq_table_index, 'struct cpufreq_frequency_table', 'frequency')
                print("%2d:%-10d" %(j, frequency), end= '', file = print_out.out_file)
                if max_freq == frequency:
                    break
        except Exception as err:
            print(err)
        print_out_str("\n")
        anomaly = Anomaly()
        anomaly.setOutputDir(ramdump.outdir)
        if max_freq != cpuinfo_max_freq:
            anomaly_str = "cpu {0} max frequency got tempered. Curr max limit : {1} actual max limit : {2}\n"\
                        .format(i, max_freq, cpuinfo_max_freq)
            anomaly.addWarning("HLOS", "dmesg_TZ.txt", anomaly_str)
        if min_freq != cpuinfo_min_freq:
            anomaly_str = "cpu {0} min frequency got tempered. Curr min limit : {1} actual min limit : {2}\n" \
                .format(i, min_freq, cpuinfo_min_freq)
            anomaly.addWarning("HLOS", "dmesg_TZ.txt", anomaly_str)
        try:
            arch_scale = ramdump.read_int(ramdump.address_of('cpu_scale') + ramdump.per_cpu_offset(i))
            cap_orig = ramdump.read_structure_field(rq_addr, 'struct rq', 'cpu_capacity_orig')
            # INFO: Since kernel v6.7 merged the upstream kernel commit 7bc263840bc3 ("sched/topology: Consolidate
            #       and clean up access to a CPU's max compute capacity"), cpu_capacity_orig has been removed from
            #       rq and replaced by arch_scale_cpu_capacity.
            if cap_orig is None:
                cap_orig = arch_scale
            print_out_str("\tCapacity: capacity_orig:{0}, cur_cap:{1}, arch_scale:{2}\n".format(cap_orig, curr_cap, arch_scale))
        except Exception as err:
            print(err)


@register_parser('--sched-info', 'Verify scheduler\'s various parameter status')
class Schedinfo(RamParser):
    def parse(self):
        global cpu_online_bits
        # Active cpu check verified by default!
        #verify_active_cpus(self.ramdump)

        # print cpufreq info
        dump_cpufreq_data(self.ramdump)

        # verify nr_migrates
        sched_nr_migrate = self.ramdump.read_u32('sysctl_sched_nr_migrate')
        if sched_nr_migrate is not None and (sched_nr_migrate != DEFAULT_MIGRATION_NR):
            print_out_str("*" * 5 + " WARNING:" + "\n")
            print_out_str("\t sysctl_sched_nr_migrate has changed!!\n")
            print_out_str("\t\t sysctl_sched_nr_migrate Default:{0} and Value in dump:{1}\n".format(DEFAULT_MIGRATION_NR, sched_nr_migrate))

        # verify migration cost
        sched_migration_cost = self.ramdump.read_u32('sysctl_sched_migration_cost')
        if (sched_migration_cost != DEFAULT_MIGRATION_COST):
            print_out_str("*" * 5 + " WARNING:" + "\n")
            print_out_str("\t sysctl_sched_migration_cost has changed!!\n")
            print_out_str("\t\tDefault: 500000 and Value in dump:{0}\n".format(sched_migration_cost))

        # verify CFS BANDWIDTH enabled
        cfs_bandwidth_enabled = self.ramdump.read_u32('sysctl_sched_cfs_bandwidth_slice')
        if cfs_bandwidth_enabled is not None:
            print_out_str("*" * 5 + " INFORMATION:" + "\n")
            print_out_str("\tCFS_BANDWIDTH is enabled in the dump!!\n")
            print_out_str("\tBandwidth slice: {0}\n".format(cfs_bandwidth_enabled))

        #verify RT threasholds
        sched_rt_runtime = self.ramdump.read_u32('sysctl_sched_rt_runtime')
        sched_rt_period = self.ramdump.read_u32('sysctl_sched_rt_period')
        if (sched_rt_runtime != DEFAULT_RT_RUNTIME) or (sched_rt_period != DEFAULT_RT_PERIOD):
            print_out_str("*" * 5 + " WARNING:" + "\n")
            print_out_str("\t RT sysctl knobs may have changed!!\n")
            print_out_str("\t\t sysctl_sched_rt_runtime Default:{0} and Value in dump:{1}\n".format(DEFAULT_RT_RUNTIME, sched_rt_runtime))
            print_out_str("\t\t sysctl_sched_rt_period Default:{0} and Value in dump:{1}\n".format(DEFAULT_RT_PERIOD, sched_rt_period))

        # verify rq root domain
        runqueues_addr = self.ramdump.address_of('runqueues')
        rd_offset = self.ramdump.field_offset('struct rq', 'rd')
        sd_offset = self.ramdump.field_offset('struct rq', 'sd')
        def_rd_addr = self.ramdump.address_of('def_root_domain')

        try:
            for cpu in (mask_bitset_pos(cpu_online_bits)):
                rq_addr = runqueues_addr + self.ramdump.per_cpu_offset(cpu)
                rd = self.ramdump.read_word(rq_addr + rd_offset)
                sd = self.ramdump.read_word(rq_addr + sd_offset)
                if rd == def_rd_addr :
                    print_out_str("*" * 5 + " WARNING:" + "\n")
                    print_out_str("Online cpu:{0} has attached to default sched root domain {1:x}\n".format(cpu, def_rd_addr))
                if sd == 0 or sd == None:
                    print_out_str("*" * 5 + " WARNING:" + "\n")
                    print_out_str("Online cpu:{0} has Null sched_domain!!\n".format(cpu))
        except Exception as err:
            print(err)

        # verify uclamp_util_max/min
        sched_uclamp_util_min = self.ramdump.read_u32('sysctl_sched_uclamp_util_min')
        sched_uclamp_util_max = self.ramdump.read_u32('sysctl_sched_uclamp_util_max')
        if sched_uclamp_util_min is not None and ((sched_uclamp_util_min != SCHED_CAPACITY_SCALE) or (sched_uclamp_util_max != SCHED_CAPACITY_SCALE)):
            print_out_str("*" * 5 + " WARNING:" + "\n")
            print_out_str("\t\t sysctl_sched_uclamp_util_min Default:{0} and Value in dump:{1}\n".format(SCHED_CAPACITY_SCALE, sched_uclamp_util_min))
            print_out_str("\t\t sysctl_sched_uclamp_util_max Default:{0} and Value in dump:{1}\n".format(SCHED_CAPACITY_SCALE, sched_uclamp_util_max))
        dump_rq_lock_information(self.ramdump)
        dump_isolation_data(self.ramdump)
        print_out.out_file.flush()
        os.fsync(print_out.out_file.fileno())
