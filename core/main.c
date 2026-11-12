#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "mongoose.h"

// Esta função é chamada toda vez que acontece algo numa conexão.
static void handler(struct mg_connection *c, int ev, void *ev_data) {
    if (ev != MG_EV_HTTP_MSG) return;
    struct mg_http_message *hm = (struct mg_http_message *) ev_data;

    mg_http_reply(c, 200, "", "ok\n");   // responde logo, pro wppconnect não ficar esperando

    char *event = mg_json_get_str(hm->body, "$.event");   // retorna cópia no heap
    if (event && strcmp(event, "onmessage") == 0) {
        char *body = mg_json_get_str(hm->body, "$.body");
        char *from = mg_json_get_str(hm->body, "$.from");
        bool from_me = false;
        mg_json_get_bool(hm->body, "$.fromMe", &from_me);

        if (body && body[0] && !from_me) {
            printf("mensagem de %s: %s\n", from ? from : "?", body);
        }
        free(body);   // toda string de mg_json_get_str precisa de free
        free(from);
    }
    free(event);
}

int main(void) {
    mg_log_set(MG_LL_ERROR);
    setvbuf(stdout, NULL, _IOLBF, 0);   // faz o log aparecer na hora no docker logs

    struct mg_mgr mgr;                  // o "gerenciador" de conexões
    mg_mgr_init(&mgr);
    mg_http_listen(&mgr, "http://0.0.0.0:3000", handler, NULL);
    printf("escutando na porta 3000\n");

    for (;;) mg_mgr_poll(&mgr, 1000);   // loop infinito: espera eventos
}