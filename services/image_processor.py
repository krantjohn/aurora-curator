import io
import logging
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
from PIL import Image
import imagehash
from config import THUMBNAIL_SIZE, PHASH_SIMILARITY_THRESHOLD

logger = logging.getLogger("anime_gallery.services.image_processor")

class ImageProcessor:
    @staticmethod
    def process_image_all(image_bytes: bytes, thumb_dest_path: Path) -> Tuple[int, int, int, str, str, str]:
        """
        Unified single-pass image processor:
        Computes dimensions, hashes (pHash, dHash, aHash), and generates WebP thumbnail in a single pass.
        Returns: (width, height, file_size, phash, dhash, ahash)
        """
        thumb_dest_path.parent.mkdir(parents=True, exist_ok=True)
        file_size = len(image_bytes)

        with Image.open(io.BytesIO(image_bytes)) as img:
            width, height = img.size

            # Compute perceptual hashes on RGB copy
            phash_str = str(imagehash.phash(img))
            dhash_str = str(imagehash.dhash(img))
            ahash_str = str(imagehash.average_hash(img))

            # Generate lightweight WebP thumbnail
            thumb_img = img.copy()
            if thumb_img.mode in ("RGBA", "LA", "P"):
                thumb_img = thumb_img.convert("RGBA")
            else:
                thumb_img = thumb_img.convert("RGB")

            thumb_img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.BILINEAR)
            thumb_img.save(str(thumb_dest_path), format="WEBP", quality=82, method=2)

        return width, height, file_size, phash_str, dhash_str, ahash_str

    @staticmethod
    def is_duplicate(phash1: str, phash2: str, threshold: int = PHASH_SIMILARITY_THRESHOLD) -> bool:
        """Determines if two images are perceptual duplicates based on Hamming distance."""
        if not phash1 or not phash2:
            return False
        try:
            h1 = imagehash.hex_to_hash(phash1)
            h2 = imagehash.hex_to_hash(phash2)
            return (h1 - h2) <= threshold
        except Exception:
            return False
