# Copyright (C) 2013-2014 eNovance SAS <licensing@enovance.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import unittest
from unittest import mock

from hardware import detect
from hardware.tests.results import detect_results
from hardware.tests.utils import sample


@mock.patch('hardware.detect_utils.get_ethtool_status',
            lambda *args, **kwargs: [])
@mock.patch('socket.inet_ntoa', lambda *args, **kwargs: '255.255.255.0')
@mock.patch('fcntl.ioctl', lambda *args, **kwargs: [])
@mock.patch('hardware.detect_utils.get_lld_status',
            lambda *args, **kwargs: [])
class TestDetect(unittest.TestCase):

    def test_get_cidr(self):
        self.assertEqual(detect.get_cidr('255.255.0.0'), '16')

    @mock.patch('hardware.detect._from_file', side_effect=IOError())
    @mock.patch('hardware.detect_utils.output_lines',
                side_effect=[
                    sample('lscpu').split('\n'),
                    sample('lscpux').split('\n')])
    def test_get_cpus(self, mock_output_lines, mock_throws_ioerror):
        hw = []
        detect.get_cpus(hw)
        self.assertEqual(hw, detect_results.GET_CPUS_RESULT)
        calls = []
        calls.append(mock.call('/sys/devices/system/cpu/smt/control'))
        # Once per socket
        for i in range(2):
            calls.append(mock.call('/sys/devices/system/cpu/cpufreq/boost'))
        # Once per processor
        for i in range(1):
            calls.append(mock.call(('/sys/devices/system/cpu/cpufreq/'
                                    'policy{}/scaling_governor'.format(i))))
            calls.append(mock.call(('/sys/devices/system/cpu/cpu{}/cpufreq/'
                                    'scaling_governor'.format(i))))
        # NOTE(tonyb): We can't use assert_has_calls() because it's too
        # permissive.  We want an exact match
        self.assertEqual(calls, mock_throws_ioerror.mock_calls)

    @mock.patch('hardware.detect._from_file', side_effect=IOError())
    @mock.patch('hardware.detect_utils.output_lines',
                side_effect=[
                    sample('lscpu-7302').split('\n'),
                    sample('lscpu-7302x').split('\n')])
    def test_get_cpus_7302(self, mock_output_lines, mock_throws_ioerror):
        self.maxDiff = None
        hw = []
        detect.get_cpus(hw)
        self.assertEqual(hw, detect_results.GET_CPUS_7302_RESULT)

    @mock.patch('hardware.detect._from_file', side_effect=IOError())
    @mock.patch('hardware.detect_utils.output_lines',
                side_effect=[
                    sample('lscpu-vm').split('\n'),
                    sample('lscpu-vmx').split('\n'),
                    ('powersave',),
                    ('powersave',)])
    def test_get_cpus_vm(self, mock_output_lines, mock_throws_ioerror):
        hw = []
        detect.get_cpus(hw)
        self.assertEqual(hw, detect_results.GET_CPUS_VM_RESULT)
        calls = []
        calls.append(mock.call('/sys/devices/system/cpu/smt/control'))
        # Once per socket
        for i in range(1):
            calls.append(mock.call('/sys/devices/system/cpu/cpufreq/boost'))
        # Once per processor
        for i in range(2):
            calls.append(mock.call(('/sys/devices/system/cpu/cpufreq/'
                                    'policy{}/scaling_governor'.format(i))))
            calls.append(mock.call(('/sys/devices/system/cpu/cpu{}/cpufreq/'
                                    'scaling_governor'.format(i))))
        # NOTE(tonyb): We can't use assert_has_calls() because it's too
        # permissive.  We want an exact match
        self.assertEqual(calls, mock_throws_ioerror.mock_calls)

    @mock.patch('hardware.detect._from_file', side_effect=IOError())
    @mock.patch('hardware.detect_utils.output_lines',
                side_effect=[
                    sample('lscpu_aarch64').split('\n'),
                    sample('lscpux_aarch64').split('\n'),
                    ('powersave',),
                    ('powersave',)])
    def test_get_cpus_aarch64(self, mock_output_lines, mock_throws_ioerror):
        self.maxDiff = None
        hw = []
        detect.get_cpus(hw)
        self.assertEqual(hw, detect_results.GET_CPUS_AARCH64_RESULT)
        calls = []
        calls.append(mock.call('/sys/devices/system/cpu/smt/control'))
        # Once per socket
        for i in range(4):
            calls.append(mock.call('/sys/devices/system/cpu/cpufreq/boost'))
        # Once per processor
        for i in range(8):
            calls.append(mock.call(('/sys/devices/system/cpu/cpufreq/'
                                    'policy{}/scaling_governor'.format(i))))
            calls.append(mock.call(('/sys/devices/system/cpu/cpu{}/cpufreq/'
                                    'scaling_governor'.format(i))))
        # NOTE(tonyb): We can't use assert_has_calls() because it's too
        # permissive.  We want an exact match
        self.assertEqual(calls, mock_throws_ioerror.mock_calls)

    @mock.patch('hardware.detect._from_file', side_effect=IOError())
    @mock.patch('hardware.detect_utils.output_lines',
                side_effect=[
                    sample('lscpu_ppc64le').split('\n'),
                    sample('lscpux_ppc64le').split('\n')])
    def test_get_cpus_ppc64le(self, mock_output_lines, mock_throws_ioerror):
        hw = []
        detect.get_cpus(hw)
        self.assertEqual(hw, detect_results.GET_CPUS_PPC64LE)
        calls = []
        calls.append(mock.call('/sys/devices/system/cpu/smt/control'))
        # Once per socket
        for i in range(2):
            calls.append(mock.call('/sys/devices/system/cpu/cpufreq/boost'))
        # Once per processor
        for i in range(144):
            calls.append(mock.call(('/sys/devices/system/cpu/cpufreq/'
                                    'policy{}/scaling_governor'.format(i))))
            calls.append(mock.call(('/sys/devices/system/cpu/cpu{}/cpufreq/'
                                    'scaling_governor'.format(i))))
        # NOTE(tonyb): We can't use assert_has_calls() because it's too
        # permissive.  We want an exact match
        self.assertEqual(calls, mock_throws_ioerror.mock_calls)

    @mock.patch('hardware.detect_utils.cmd',
                return_value=(0, sample('dmesg')),
                autospec=True)
    def test_parse_dmesg(self, mock_cmd):
        hw = []
        detect.parse_dmesg(hw)
        self.assertEqual(hw, [('ahci', '0000:00:1f.2:', 'flags',
                               '64bit apst clo ems led '
                               'ncq part pio slum sntf')])

    @mock.patch('hardware.detect_utils.cmd', return_value=(0, 4))
    @mock.patch('hardware.detect_utils.get_uuid',
                return_value='83462C81-52BA-11CB-870F')
    @mock.patch('hardware.detect.get_cpus', return_value='[]')
    @mock.patch('hardware.detect_utils.output_lines',
                side_effect=[
                    ('Ubuntu',),
                    ('Ubuntu 14.04 LTS',),
                    ('3.13.0-24-generic',),
                    ('x86_64',),
                    ('BOOT_IMAGE=/boot/vmlinuz',)])
    def test_detect_system_3(self, mock_cmd, mock_get_uuid, mock_get_cpus,
                             mock_output_lines):
        result = []
        detect.detect_system(result, sample('lshw3'))
        self.assertEqual(result, detect_results.DETECT_SYSTEM3_RESULT)

    @mock.patch('hardware.detect_utils.cmd', return_value=(0, 4))
    @mock.patch('hardware.detect_utils.get_uuid',
                return_value='83462C81-52BA-11CB-870F')
    @mock.patch('hardware.detect.get_cpus', return_value='[]')
    @mock.patch('hardware.detect_utils.output_lines',
                side_effect=[
                    ('Ubuntu',),
                    ('Ubuntu 14.04 LTS',),
                    ('3.13.0-24-generic',),
                    ('x86_64',),
                    ('BOOT_IMAGE=/boot/vmlinuz',)])
    def test_detect_system_2(self, mock_cmd, mock_get_uuid, mock_get_cpus,
                             mock_output_lines):
        result = []
        detect.detect_system(result, sample('lshw2'))
        self.assertEqual(result, detect_results.DETECT_SYSTEM2_RESULT)

    @mock.patch('hardware.detect_utils.cmd', return_value=(0, 7))
    @mock.patch('hardware.detect_utils.get_uuid',
                return_value='83462C81-52BA-11CB-870F')
    @mock.patch('hardware.detect.get_cpus', return_value='[]')
    @mock.patch('hardware.detect_utils.output_lines',
                side_effect=[
                    ('Ubuntu',),
                    ('Ubuntu 14.04 LTS',),
                    ('3.13.0-24-generic',),
                    ('x86_64',),
                    ('BOOT_IMAGE=/boot/vmlinuz',)
                ])
    def test_detect_system(self, mock_cmd, mock_get_uuid, mock_get_cpus,
                           mock_output_lines):
        result = []
        detect.detect_system(result, sample('lshw'))
        self.assertEqual(result, detect_results.DETECT_SYSTEM_RESULT)

    def test_get_value(self):
        self.assertEqual(detect._get_value([('a', 'b', 'c', 'd')],
                                           'a', 'b', 'c'), 'd')

    def test_fix_bad_serial_zero(self):
        hwl = [('system', 'product', 'serial', '0000000000')]
        detect.fix_bad_serial(hwl, 'uuid', '', '')
        self.assertEqual(detect._get_value(hwl, 'system', 'product', 'serial'),
                         'uuid')

    def test_fix_bad_serial_mobo(self):
        hwl = [('system', 'product', 'serial', '0123456789')]
        detect.fix_bad_serial(hwl, '', 'mobo', '')
        self.assertEqual(detect._get_value(hwl, 'system', 'product', 'serial'),
                         'mobo')

    @mock.patch.object(detect, 'Popen')
    @mock.patch('os.environ.copy')
    def test_detect_auxv_x86_succeed(self, mock_environ_copy, mock_popen):
        test_data = {
            'AT_HWCAP': ('hwcap', 'bfebfbff'),
            'AT_HWCAP2': ('hwcap2', '0x0'),
            'AT_PAGESZ': ('pagesz', '4096'),
            'AT_FLAGS': ('flags', '0x0'),
            'AT_PLATFORM': ('platform', 'x86_64'),
        }

        process_mock = mock.Mock()
        attrs = {'communicate.return_value': (
            sample('auxv_x86').encode('utf-8'), None)}
        process_mock.configure_mock(**attrs)
        mock_popen.return_value = process_mock

        hw = []
        detect.detect_auxv(hw)

        # NOTE(mrda): x86 doesn't have AUXV_OPT_FLAGS
        for k in detect.AUXV_FLAGS:
            t = ('hw', 'auxv', test_data[k][0], test_data[k][1])
            self.assertTrue(t in hw)

    @mock.patch.object(detect, 'Popen')
    @mock.patch('os.environ.copy')
    def test_detect_auxv_ppc8_succeed(self, mock_environ_copy, mock_popen):
        test_data = {
            'AT_HWCAP': ('hwcap',
                         'true_le archpmu vsx arch_2_06 dfp ic_snoop smt '
                         'mmu fpu altivec ppc64 ppc32'),
            'AT_HWCAP2': ('hwcap2', 'htm-nosc vcrypto tar isel ebb dscr '
                          'htm arch_2_07'),
            'AT_PAGESZ': ('pagesz', '65536'),
            'AT_FLAGS': ('flags', '0x0'),
            'AT_PLATFORM': ('platform', 'power8'),
            'AT_BASE_PLATFORM': ('base_platform', 'power8'),
        }

        process_mock = mock.Mock()
        attrs = {'communicate.return_value': (
            sample('auxv_ppc8').encode('utf-8'), None)}
        process_mock.configure_mock(**attrs)
        mock_popen.return_value = process_mock

        hw = []
        detect.detect_auxv(hw)

        ppc_flags = detect.AUXV_FLAGS + detect.AUXV_OPT_FLAGS
        for k in ppc_flags:
            t = ('hw', 'auxv', test_data[k][0], test_data[k][1])
            self.assertTrue(t in hw)
