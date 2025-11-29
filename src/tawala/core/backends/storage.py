from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from vercel.blob import BlobClient


@deconstructible
class VercelBlobStorage(Storage):
    """Custom storage backend for Vercel Blob."""

    token = getattr(settings, "STORAGE_TOKEN", "")

    def __init__(self):
        self.client = BlobClient(self.token)

    def _save(self, name, content):
        """Upload file to Vercel Blob"""
        file_content = content.read()

        result = self.client.put(
            name,
            file_content,
            access="public",
            add_random_suffix=True,  # This ensures unique filenames
            content_type=content.content_type
            if hasattr(content, "content_type")
            else None,
        )

        # Return the pathname for Tawala
        return result.pathname

    def _open(self, name, mode="rb"):
        """Download file from Vercel Blob"""
        # List to find the blob
        listing = self.client.list_objects(prefix=name, limit=1)

        if not listing.blobs:
            raise FileNotFoundError(f"File {name} not found.")

        # Get the content
        content = self.client.get(listing.blobs[0].url)

        return ContentFile(content, name=name)

    def delete(self, name):
        """Delete file from Vercel Blob"""
        listing = self.client.list_objects(prefix=name, limit=1)

        if listing.blobs:
            self.client.delete([listing.blobs[0].url])

    def exists(self, name):
        """Check if file exists in Vercel Blob"""
        listing = self.client.list_objects(prefix=name, limit=1)
        return len(listing.blobs) > 0

    def url(self, name):
        """Return public URL for the file"""
        listing = self.client.list_objects(prefix=name, limit=1)

        if not listing.blobs:
            # Raise an exception instead of returning None
            raise ValueError(f"File {name} not found in Vercel Blob storage")

        return listing.blobs[0].url

    def size(self, name):
        """Return file size"""
        listing = self.client.list_objects(prefix=name, limit=1)

        if not listing.blobs:
            return 0

        return listing.blobs[0].size

    def get_valid_name(self, name):
        """Return a filename suitable for use with the storage system"""
        return name

    def get_available_name(self, name, max_length=None):
        """Return a filename that's free on the storage system"""
        # Vercel Blob handles uniqueness with add_random_suffix
        return name
