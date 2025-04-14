REGISTRY = {}
IN_MEMORY_REGISTRY = {}


def register(interface, registry=REGISTRY):
    """
    Decorator to register a repository implementation.
    """

    def decorator(cls):
        if interface in registry:
            raise ValueError(f"Repository {interface} already registered")
        registry[interface] = cls
        return cls

    return decorator
