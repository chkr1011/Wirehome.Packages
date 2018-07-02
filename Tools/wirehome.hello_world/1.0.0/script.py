def main(parameters):
    """Creates the welcome message and returns it.
        Args:
            ["name"] = The name which should be used in the welcome message.

        Returns:
            The welcome message as str.
    """

    name = "world"
    if "name" in parameters:
        name = parameters["name"]

    return "hello " + name