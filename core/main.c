#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <curl/curl.h>
#include "mongoose.h"
#include "services/filter_service.h"

static void process_webhook(struct mg_str json)
{
    char *event = mg_json_get_str(json, "$.event");
    if (event && strcmp(event, "onmessage") == 0)
    {
        char *body = mg_json_get_str(json, "$.body");
        char *from = mg_json_get_str(json, "$.from");
        bool from_me = false;
        mg_json_get_bool(json, "$.fromMe", &from_me);

        if (body && body[0] && !from_me)
        {
            filter_process(from, body);
        }
        free(body);
        free(from);
    }
    free(event);
}

static void handler(struct mg_connection *c, int ev, void *ev_data)
{
    if (ev != MG_EV_HTTP_MSG)
        return;
    struct mg_http_message *hm = (struct mg_http_message *)ev_data;

    if (mg_match(hm->uri, mg_str("/ping"), NULL))
    {
        mg_http_reply(c, 200, "", "pong\n");
    }
    else if (mg_match(hm->uri, mg_str("/webhook"), NULL))
    {
        mg_http_reply(c, 200, "", "ok\n");
        process_webhook(hm->body);
    }
    else
    {
        mg_http_reply(c, 404, "", "nao encontrado\n");
    }
}

int main(void)
{
    mg_log_set(MG_LL_ERROR);
    setvbuf(stdout, NULL, _IOLBF, 0);
    curl_global_init(CURL_GLOBAL_DEFAULT); // novo: liga a libcurl, uma vez só

    struct mg_mgr mgr;
    mg_mgr_init(&mgr);
    mg_http_listen(&mgr, "http://0.0.0.0:3000", handler, NULL);
    printf("escutando na porta 3000\n");

    for (;;)
        mg_mgr_poll(&mgr, 1000);
}