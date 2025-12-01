class CLISetup:
    """A class to represent the state of a CLI setup process."""

    def __init__(self):
        self.is_successful: bool = False

    @classmethod
    def setsuccessful(cls):
        cls.is_successful = True
