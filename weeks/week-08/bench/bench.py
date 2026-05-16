import sys
import time
from pathlib import Path

import grpc
import httpx

APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

import service_pb2
import service_pb2_grpc


REST_URL = "http://localhost:8227/sessions"
GRPC_URL = "localhost:50051"
REQUESTS = 1000


def bench_rest():
    start = time.perf_counter()

    with httpx.Client(timeout=5) as client:
        for _ in range(REQUESTS):
            client.get(REST_URL)

    return time.perf_counter() - start


def bench_grpc():
    start = time.perf_counter()

    with grpc.insecure_channel(GRPC_URL) as channel:
        stub = service_pb2_grpc.SessionsServiceStub(channel)
        stub.CreateSession(service_pb2.CreateSessionRequest(name="demo", ip="127.0.0.1"))

        for _ in range(REQUESTS):
            stub.GetSession(service_pb2.GetSessionRequest(id=1))

    return time.perf_counter() - start


def main():
    rest_time = bench_rest()
    grpc_time = bench_grpc()

    print(f"REST: {rest_time:.4f} sec")
    print(f"gRPC: {grpc_time:.4f} sec")


if __name__ == "__main__":
    main()
