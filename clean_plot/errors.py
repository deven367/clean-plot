# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/07_errors.ipynb.

# %% auto 0
__all__ = ["MyException"]

# %% ../nbs/07_errors.ipynb 3
class MyException(Exception):
    def __init__(self, message):
        super().__init__(message)

        self.message = message

    def __str__(self):
        return self.message


# %% ../nbs/07_errors.ipynb 4
import inspect
