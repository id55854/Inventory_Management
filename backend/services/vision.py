"""MediaPipe vision pipeline — stub for prototype (wire Section 6 later)."""


class ShelfVisionPipeline:
    """Placeholder until MediaPipe model is configured."""

    def detect_products(self, image_bytes: bytes) -> list[dict]:
        return []

    def estimate_occupancy(self, detections: list[dict]) -> float:
        return 0.0 if not detections else 50.0

    def identify_issues(
        self, detections: list, store_id: int, aisle_id: int | None
    ) -> list[dict]:
        return []
