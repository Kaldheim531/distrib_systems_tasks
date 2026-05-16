from concurrent import futures
import time

import grpc
import service_pb2
import service_pb2_grpc


sessions = []
last_id = 0


class SessionsService(service_pb2_grpc.SessionsServiceServicer):
    def CreateSession(self, request, context):
        global last_id

        last_id += 1
        session = service_pb2.Session(
            id=last_id,
            name=request.name,
            ip=request.ip,
        )
        sessions.append(session)
        return session

    def GetSession(self, request, context):
        for session in sessions:
            if session.id == request.id:
                return session

        context.abort(grpc.StatusCode.NOT_FOUND, "Session not found")

    def SubscribeSessions(self, request, context):
        limit = request.limit or 3

        for index in range(limit):
            session_id = index + 1
            yield service_pb2.SessionUpdate(
                id=session_id,
                name=f"session-{session_id}",
                ip=f"127.0.0.{session_id}",
                event="created",
            )
            time.sleep(0.1)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_SessionsServiceServicer_to_server(SessionsService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
