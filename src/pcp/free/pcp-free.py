#!/usr/bin/env pmpython
#
# Copyright (C) 2014-2018 Red Hat.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# pylint: disable=missing-docstring,bad-continuation,bad-whitespace
#
""" Display amount of free and used memory in the system """

import sys
from pcp import pmapi
from cpmapi import PM_TYPE_U64, PM_CONTEXT_ARCHIVE, PM_SPACE_KBYTE

if sys.version >= '3':
    long = int  # python2 to python3 portability (no long() in python3)

class Free(object):
    """ Gives a short summary of kernel virtual memory information,
        in a variety of formats, possibly sampling in a loop.

        Knows about some of the default PCP arguments - can function
        using remote hosts or historical data, using the timezone of
        the metric source, at an offset within an archive, and so on.
    """

    def __init__(self):
        """ Construct object - prepare for command line handling """
        self.count = 0       # number of samples to report
        self.pause = None    # time interval to pause between samples
        self.shift = 10      # bitshift conversion between B/KB/MB/GB
        self.show_wide = 0
        self.show_high = 0
        self.show_total = 0
        self.show_compat = 0
        self.opts = self.options()
        self.interval = pmapi.timeval()
        self.context = None

    def options(self):
        """ Setup default command line argument option handling """
        opts = pmapi.pmOptions()
        opts.pmSetOptionCallback(self.option)
        opts.pmSetOverrideCallback(self.override)
        opts.pmSetShortOptions("bc:gklmrots:Vw?")
        opts.pmSetLongOptionHeader("Options")
        opts.pmSetLongOption("bytes", 0, 'b', '', "show output in bytes")
        opts.pmSetLongOption("kilobytes", 0, 'k', '', "show output in KB")
        opts.pmSetLongOption("megabytes", 0, 'm', '', "show output in MB")
        opts.pmSetLongOption("gigabytes", 0, 'g', '', "show output in GB")
        opts.pmSetLongOption("terabytes", 0, 'r', '', "show output in TB")
        opts.pmSetLongOption("", 0, 'o', '',
                             "use old format (-/+buffers/cache line)")
        opts.pmSetLongOption("lohi", 0, 'l', '',
                             "show detailed low and high memory statistics")
        opts.pmSetLongOption("total", 0, 't', '',
                             "display total for RAM + swap")
        opts.pmSetLongOption("count", 1, 'c', "COUNT",
                             "repeat printing COUNT times, then exit")
        opts.pmSetLongOption("samples", 1, 'c', "COUNT",
                             "number of samples (alias for --count)")
        opts.pmSetLongOption("seconds", 1, 's', "DELTA",
                             "repeat printing every DELTA seconds")
        opts.pmSetLongOption("interval", 1, 's', "DELTA",
                             "sampling interval (alias for --seconds)")
        opts.pmSetLongOptionVersion()
        opts.pmSetLongOptionHelp()
        return opts

    def override(self, opt):
        """ Override a few standard PCP options to match free(1) """
        # pylint: disable=R0201
        if opt in ('g', 's', 't'):
            return 1
        return 0

    def option(self, opt, optarg, index):
        """ Perform setup for an individual command line option """
        # pylint: disable=W0613
        if opt == 'b':
            self.shift = 0
        elif opt == 'k':
            self.shift = 10
        elif opt == 'm':
            self.shift = 20
        elif opt == 'g':
            self.shift = 30
        elif opt == 'r':
            self.shift = 40
        elif opt == 'o':
            self.show_compat = 1
        elif opt == 'w':
            self.show_wide = 1
        elif opt == 'l':
            self.show_high = 1
        elif opt == 't':
            self.show_total = 1
        elif opt == 's':
            self.pause = optarg
            self.opts.pmSetOptionInterval(optarg)
            self.interval = self.opts.pmGetOptionInterval()
        elif opt == 'c':
            self.opts.pmSetOptionSamples(optarg)
            self.count = self.opts.pmGetOptionSamples()

    def scale(self, value):
        """ Convert a given value in kilobytes into display units """
        return long(value << 10) >> self.shift

    def extract(self, descs, result):
        """ Extract the set of metric values from a given pmResult """
        values = []
        for index, desc in enumerate(descs):
            if result.contents.get_numval(index) > 0:
                atom = self.context.pmExtractValue(
                                result.contents.get_valfmt(index),
                                result.contents.get_vlist(index, 0),
                                desc.contents.type, PM_TYPE_U64)
                atom = self.context.pmConvScale(PM_TYPE_U64, atom, descs, index,
                                pmapi.pmUnits(1, 0, 0, PM_SPACE_KBYTE, 0, 0))
                values.append(long(atom.ull))
            else:
                values.append(long(0))
        return values

    def execute(self):
        """ Using a PMAPI context (could be either host or archive),
            fetch and report a fixed set of values related to memory.
        """
        metrics = ('mem.physmem',
                   'mem.util.free',  'mem.util.shmem',
                   'mem.util.bufmem',  'mem.util.cached',
                   'mem.util.highFree',  'mem.util.highTotal',
                   'mem.util.lowFree',  'mem.util.lowTotal',
                   'mem.util.swapFree',  'mem.util.swapTotal',
                   'mem.util.available',  'mem.util.slabReclaimable')

        pmids = self.context.pmLookupName(metrics)
        descs = self.context.pmLookupDescs(pmids)

        if self.pause is None and self.count == 0:
            self.count = 1
        if self.pause is not None and self.count == 0:
            self.count = -1

        while self.count != 0:
            result = self.context.pmFetch(pmids)
            values = self.extract(descs, result)
            self.context.pmFreeResult(result)
            self.report(values)
            if self.pause is not None:
                print('') # empty line
                sys.stdout.flush()
                if self.count > 0:
                    self.count -= 1
                if self.count == 0:
                    break
                if self.context.type != PM_CONTEXT_ARCHIVE:
                    self.context.pmtimevalSleep(self.interval)
            elif self.count == 1 and self.pause is None:
                break
            elif self.count > 0:
                self.count -= 1

    def report(self, values):
        """ Given the set of metric values report them in free(1) form """
        physmem = values[0]
        free = values[1]
        shared = values[2]
        buffers = values[3]
        cached = values[4]
        highfree = values[5]
        hightotal = values[6]
        lowfree = values[7]
        lowtotal = values[8]
        swapfree = values[9]
        swaptotal = values[10]
        available = values[11]
        slabreclaim = values[12]

        used = physmem - free - buffers - cached - slabreclaim
        cache = cached + slabreclaim
        swapused = swaptotal - swapfree

        # low == main memory, except with large-memory support
        if lowtotal == 0:
            lowtotal = physmem
            lowfree = free

        if self.show_wide:
            columns = ('total', 'used', 'free', 'shared', 'buffers', 'cache', 'available')
            print("%19s %11s %11s %11s %11s %11s %11s" % columns)
            print("%-7s %11Lu %11Lu %11Lu %11Lu %11Lu %11Lu %11Lu" % ('Mem:',
                self.scale(physmem), self.scale(used), self.scale(free),
                self.scale(shared), self.scale(buffers), self.scale(cache),
                self.scale(available)))
        else:
            columns = ('total', 'used', 'free', 'shared', 'buff/cache', 'available')
            print("%19s %11s %11s %11s %11s %11s" % columns)
            print("%-7s %11Lu %11Lu %11Lu %11Lu %11Lu %11Lu" % ('Mem:',
                self.scale(physmem), self.scale(used), self.scale(free),
                self.scale(shared), self.scale(buffers + cache),
                self.scale(available)))

        if self.show_high:
            print("%-7s %11Lu %11Lu %11Lu" % ('Low:', self.scale(lowtotal),
                    self.scale(lowtotal - lowfree), self.scale(lowtotal)))
            print("%-7s %11Lu %11Lu %11Lu" % ('High:', self.scale(hightotal),
                    self.scale(hightotal - highfree), self.scale(highfree)))
        if self.show_compat != 0:
            cache = buffers + cached
            print("%s:  %11Lu %11Lu" % ('-/+ buffers/cache',
                    self.scale(used - cache), self.scale(free + cache)))

        print("%-7s %11Lu %11Lu %11Lu" % ('Swap', self.scale(swaptotal),
                self.scale(swapused), self.scale(swapfree)))

        if self.show_total == 1:
            print("%-7s %11Lu %11Lu %11Lu" % ('Total',
                    self.scale(physmem + swaptotal),
                    self.scale(used + swapused), self.scale(free + swapfree)))

    def connect(self):
        """ Establish a PMAPI context to archive, host or local, via args """
        self.context = pmapi.pmContext.fromOptions(self.opts, sys.argv)

if __name__ == '__main__':
    try:
        FREE = Free()
        FREE.connect()
        FREE.execute()
    except pmapi.pmErr as error:
        print("%s: %s" % (error.progname(), error.message()))
    except pmapi.pmUsageErr as usage:
        usage.message()
    except KeyboardInterrupt:
        pass
