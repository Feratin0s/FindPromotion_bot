#ifndef URL_SERVICE_H
#define URL_SERVICE_H
#include <stddef.h>

// Acha a próxima URL em text e copia pra out. Devolve onde parou, ou NULL se não achou.
const char *url_find_next(const char *text, char *out, size_t out_size);

// Segue os redirecionamentos e escreve a URL final em out. 0 = ok, -1 = erro.
int url_resolve(const char *url, char *out, size_t out_size);

// Corta tudo a partir do '?' (parâmetros de rastreio/afiliado).
void url_strip_query(char *url);

#endif