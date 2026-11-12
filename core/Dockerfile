FROM alpine:3.20 AS build
RUN apk add --no-cache build-base hiredis-dev mariadb-connector-c-dev
WORKDIR /src
COPY . .
RUN gcc -O2 -Wall -o core main.c mongoose.c -lhiredis -lmariadb

FROM alpine:3.20
RUN apk add --no-cache hiredis mariadb-connector-c
COPY --from=build /src/core /core
CMD ["/core"]