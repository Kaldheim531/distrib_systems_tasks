from concurrent import futures

import grpc
import service_pb2
import service_pb2_grpc


reviews = []
last_id = 0


class ReviewsService(service_pb2_grpc.ReviewsServiceServicer):
    def CreateReview(self, request, context):
        global last_id

        last_id += 1
        review = service_pb2.Review(
            id=last_id,
            name=request.name,
            rating=request.rating,
        )
        reviews.append(review)
        return review

    def GetReview(self, request, context):
        for review in reviews:
            if review.id == request.id:
                return review

        context.abort(grpc.StatusCode.NOT_FOUND, "Review not found")

    def ListReviews(self, request, context):
        return service_pb2.ListReviewsResponse(reviews=reviews)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_ReviewsServiceServicer_to_server(ReviewsService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
