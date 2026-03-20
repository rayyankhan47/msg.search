"""Instagram export importer."""

from importers.meta_base import MetaZipImporterBase


class InstagramImporter(MetaZipImporterBase):
    """Parse Instagram message exports from a ZIP file."""

    platform = "instagram"
