import prefect


@prefect.flow
def howdy(name: str) -> str:
    return f"howdy, {name}!"
