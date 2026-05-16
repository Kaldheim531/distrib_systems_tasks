#!/usr/bin/env bash
set -e

REST_URL="${REST_URL:-http://127.0.0.1:8226/devices}"
GRPC_ADDR="${GRPC_ADDR:-localhost:50051}"
PROTO_FILE="${PROTO_FILE:-proto/service.proto}"
GRPC_CALL="${GRPC_CALL:-devices.v1.DevicesService.GetDevice}"

wrk -t1 -c1 -d30s "$REST_URL"
wrk -t2 -c10 -d30s "$REST_URL"
wrk -t4 -c100 -d30s "$REST_URL"

ghz --insecure --proto "$PROTO_FILE" --call "$GRPC_CALL" -c 1 -n 1000 "$GRPC_ADDR"
ghz --insecure --proto "$PROTO_FILE" --call "$GRPC_CALL" -c 10 -n 10000 "$GRPC_ADDR"
ghz --insecure --proto "$PROTO_FILE" --call "$GRPC_CALL" -c 100 -n 30000 "$GRPC_ADDR"
