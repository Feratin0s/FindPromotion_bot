#include <string.h>
#include <ctype.h>
#include <curl/curl.h>
#include "url_service.h"

const char *url_find_next(const char *text, char *out, size_t out_size)
{
    const char *p = strstr(text, "http://");
    const char *q = strstr(text, "https://");
    if (!p || (q && q < p))
        p = q; // pega a que aparece primeiro
    if (!p)
        return NULL;

    size_t n = 0; // copia até o primeiro espaço/quebra de linha
    while (p[n] && !isspace((unsigned char)p[n]) && n < out_size - 1)
        n++;
    while (n > 0 && strchr(".,;)", p[n - 1]))
        n--; // tira pontuação grudada no fim
    memcpy(out, p, n);
    out[n] = '\0';
    return p + n;
}

int url_resolve(const char *url, char *out, size_t out_size)
{
    CURL *h = curl_easy_init();
    if (!h)
        return -1;

    curl_easy_setopt(h, CURLOPT_URL, url);
    curl_easy_setopt(h, CURLOPT_FOLLOWLOCATION, 1L); // segue os redirecionamentos
    curl_easy_setopt(h, CURLOPT_MAXREDIRS, 5L);      // no máximo 5 saltos
    curl_easy_setopt(h, CURLOPT_TIMEOUT, 5L);        // desiste em 5 segundos
    curl_easy_setopt(h, CURLOPT_NOBODY, 1L);         // pede só os cabeçalhos (HEAD)
    curl_easy_setopt(h, CURLOPT_USERAGENT, "Mozilla/5.0");
    curl_easy_setopt(h, CURLOPT_PROTOCOLS_STR, "http,https");
    curl_easy_setopt(h, CURLOPT_REDIR_PROTOCOLS_STR, "http,https");

    int ret = -1;
    if (curl_easy_perform(h) == CURLE_OK)
    {
        char *final_url = NULL;
        long status = 0;
        curl_easy_getinfo(h, CURLINFO_EFFECTIVE_URL, &final_url);
        curl_easy_getinfo(h, CURLINFO_RESPONSE_CODE, &status);
        printf("  http status: %ld\n", status);
        if (final_url && status < 400)
        {
            strncpy(out, final_url, out_size - 1);
            out[out_size - 1] = '\0';
            ret = 0;
        }
    }
    curl_easy_cleanup(h);
    return ret;
}

void url_strip_query(char *url)
{
    char *q = strchr(url, '?');
    if (q)
        *q = '\0';
}