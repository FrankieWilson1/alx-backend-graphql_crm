import graphene


class Query(graphene.ObjectType):
    """
    A class that defines the Query type, which is the
    entry point for all queries.

    Attributes:
        hello (graphene.String): A greeting message.
    """
    hello = graphene.String(default_value="Hello, GraphQL!")


schema = graphene.Schema(query=Query)
