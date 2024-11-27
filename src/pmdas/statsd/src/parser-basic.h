/*
 * Copyright (c) 2020 Red Hat.
 * Copyright (c) 2019 Miroslav Foltýn.  All Rights Reserved.
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
#ifndef PARSER_BASIC_
#define PARSER_BASIC_

#include "parsers.h"

/**
 * Basic parser entry point
 * Parsers given buffer and populates datagram with parsed data if they are valid
 * @arg buffer - Buffer to be parsed
 * @arg datagram - Placeholder for parsed data
 * @return 1 on success, 0 on fail 
 */
extern int
basic_parser_parse(char *buffer, struct statsd_datagram** datagram);

#endif
