from typing import List
from hub.core.storage.provider import StorageProvider
from hub.core.meta.meta import Meta
from hub.util.keys import get_dataset_meta_key


class DatasetMeta(Meta):
    tensors: List

    @staticmethod
    def create(storage: StorageProvider):
        """Dataset metadata is responsible for keeping track of global tensor metadata and where tensors exist.

        Note:
            Dataset metadata that is automatically synchronized with `storage`. For more details, see the `Meta` class.
            Auto-populates `required_meta` that `Meta` accepts as an argument.

        Args:
            storage (StorageProvider): Destination of this meta. No `key` argument required, the
                dataset meta file will be added to the root of `storage`.
        """

        required_meta = {
            "tensors": [],
        }

        return DatasetMeta(get_dataset_meta_key(), storage, required_meta=required_meta)

    @staticmethod
    def load(storage: StorageProvider):
        return DatasetMeta(get_dataset_meta_key(), storage)
