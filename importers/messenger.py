"""Messenger export importer."""

from importers.meta_base import MetaZipImporterBase


class MessengerImporter(MetaZipImporterBase):
    """Parse Facebook Messenger message exports from a ZIP file."""

    platform = "messenger"
