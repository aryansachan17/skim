import strawberry
from graphql import GraphQLError
from strawberry.extensions import MaskErrors
from strawberry.fastapi import GraphQLRouter

from config import settings
from utility.base_exceptions import BaseHTTPError


@strawberry.type
class Health:
    status: str
    environment: str
    version: str


@strawberry.type
class Query:
    @strawberry.field
    def health(self) -> Health:
        return Health(
            status="ok",
            environment=settings.current_env.lower(),
            version=settings.VERSION,
        )


def should_mask_error(error: GraphQLError) -> bool:
    original = error.original_error
    if original is None:
        return False
    if isinstance(original, BaseHTTPError) and original.status_code < 500:
        return False
    return not settings.EXPOSE_ERROR_DETAILS


schema = strawberry.Schema(
    query=Query,
    extensions=[lambda: MaskErrors(should_mask_error=should_mask_error)],
)


def get_graphql_router() -> GraphQLRouter:
    return GraphQLRouter(schema, graphql_ide="graphiql" if settings.GRAPHQL_IDE else None)
