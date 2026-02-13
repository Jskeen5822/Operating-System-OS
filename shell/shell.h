#ifndef SHELL_H
#define SHELL_H

#include "../include/types.h"
#include "../include/defs.h"

/* Shell control */
void shell_start(void);
static void shell_read_command(void);
static void shell_parse_command(void);
static void shell_execute_command(void);

#endif
