class ExecutableNotFound(Exception):
    def __init__(self, target: str):
        super().__init__(f"The target command: {target} is not resolvable.")
