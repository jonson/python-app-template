from sqlmodel import SQLModel


# re-export the metadata via the __init__ file to ensure _init_models is called
METADATA = SQLModel.metadata


def _init_models():
    """
    This function is used to initialize the models.
    It's used to register the models with the SQLModel.
    """
    import importlib
    import pkgutil

    # Get the current package name and path
    package_name = __name__
    package_path = __path__

    def import_submodules(package_name, package_path):
        for _, module_name, is_pkg in pkgutil.iter_modules(package_path):
            full_module_name = f"{package_name}.{module_name}"
            module = importlib.import_module(full_module_name)
            if is_pkg:
                sub_package_path = module.__path__
                import_submodules(full_module_name, sub_package_path)

    import_submodules(package_name, package_path)


_init_models()
