from hub.util.exceptions import WindowsSharedMemoryError
import os

try:
    if os.name == "nt":
        raise WindowsSharedMemoryError
    from hub.core.storage import SharedMemoryProvider
    from .pytorch import dataset_to_pytorch
except (ImportError, WindowsSharedMemoryError):
    from .pytorch_old import dataset_to_pytorch
