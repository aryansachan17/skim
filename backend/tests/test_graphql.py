import pytest
from graphql import GraphQLError

from app.graphql_schema import should_mask_error
from utility.base_exceptions import BadRequestError, ServiceUnavailableError


def test_health_query_returns_status_and_environment(client):
    response = client.post("/graphql", json={"query": "{ health { status environment } }"})

    assert response.status_code == 200
    assert response.json() == {"data": {"health": {"status": "ok", "environment": "test"}}}


def test_query_mistakes_are_explained_to_the_client(client):
    response = client.post("/graphql", json={"query": "{ health { colour } }"})

    assert "Cannot query field 'colour'" in response.json()["errors"][0]["message"]


@pytest.mark.parametrize(
    ("original_error", "masked"),
    [
        (None, False),
        (BadRequestError("That URL is not valid."), False),
        (ServiceUnavailableError("redis at 10.0.0.5 refused"), True),
        (RuntimeError("db password=hunter2"), True),
    ],
)
def test_only_safe_errors_reach_graphql_clients(original_error, masked):
    error = GraphQLError("failure", original_error=original_error)

    assert should_mask_error(error) is masked
