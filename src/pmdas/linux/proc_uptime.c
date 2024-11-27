/*
 * Copyright (c) Red Hat 2014,2016,2020.
 * Copyright (c) International Business Machines Corp., 2002
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 * or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
 * for more details.
 */
#include <fcntl.h>
#include "linux.h"
#include "proc_uptime.h"

int
refresh_proc_uptime(proc_uptime_t *proc_uptime)
{
    char buf[MAXPATHLEN];
    int fd, n;

    memset(proc_uptime, 0, sizeof(proc_uptime_t));
    pmsprintf(buf, sizeof(buf), "%s/proc/uptime", linux_statspath);
    if ((fd = open(buf, O_RDONLY)) < 0)
	return -oserror();

    n = read(fd, buf, sizeof(buf));
    close(fd);
    if (n < 0)
	return -oserror();
    else if (n > 0)
	n--;
    buf[n] = '\0';

    sscanf(buf, "%lf %lf", &proc_uptime->uptime, &proc_uptime->idletime);
    return 0;
}
