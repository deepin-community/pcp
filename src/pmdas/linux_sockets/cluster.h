/*
 * Copyright (c) 2021 Red Hat.
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
#ifndef _CLUSTER_H
#define _CLUSTER_H

enum {
    CLUSTER_GLOBAL = 0,         /* global stats */
    CLUSTER_SS = 1,             /* per-socket stats */
    NUM_CLUSTERS
};
#endif /* _CLUSTER_H */
