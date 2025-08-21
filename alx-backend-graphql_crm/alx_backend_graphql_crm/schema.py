import graphene

class Query(graphene.ObjectType):
    """Root query for the GraphQL schema.
    """
    hello = graphene.String(default_value="hello, GraphQL!")

schema = graphene.Schema(query=Query)
