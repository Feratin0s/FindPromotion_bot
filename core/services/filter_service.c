#include <stdio.h>
#include "filter_service.h"
#include "url_service.h"

void filter_process(const char *from, const char *body) {
    printf("mensagem de %s: %s\n", from ? from : "?", body);

    char url[512], final_url[1024];
    const char *resto = body;
    while ((resto = url_find_next(resto, url, sizeof url)) != NULL) {
        printf("  link encontrado: %s\n", url);
        if (url_resolve(url, final_url, sizeof final_url) == 0) {
            printf("  link final:      %s\n", final_url);
            url_strip_query(final_url);
            printf("  link limpo:      %s\n", final_url);
        } else {
            printf("  nao consegui resolver\n");
        }
    }
}