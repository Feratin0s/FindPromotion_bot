#ifndef FILTER_SERVICE_H
#define FILTER_SERVICE_H

// Recebe a mensagem crua, acha os links e resolve cada um.
void filter_process(const char *from, const char *body);

#endif