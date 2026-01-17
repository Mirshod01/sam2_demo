# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

import io
import json
import logging
import os
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

import cv2
import numpy as np
from pycocotools.mask import decode as decode_masks

logger = logging.getLogger(__name__)


class YOLOExporter:
    """Export SAM2 tracking results to YOLO format."""

    def __init__(self):
        pass

    def mask_to_bbox(self, rle_mask: Dict[str, Any]) -> Tuple[float, float, float, float]:
        """Convert RLE mask to YOLO bounding box (normalized)."""
        # Decode RLE mask to binary mask
        mask = decode_masks(rle_mask)

        # Find all non-zero points
        rows, cols = np.where(mask > 0)

        if len(rows) == 0 or len(cols) == 0:
            return (0.0, 0.0, 0.0, 0.0)

        # Get bounding box coordinates
        min_row, max_row = rows.min(), rows.max()
        min_col, max_col = cols.min(), cols.max()

        # Get image dimensions
        img_height, img_width = rle_mask['size']

        # Calculate bounding box
        bbox_x = min_col
        bbox_y = min_row
        bbox_width = max_col - min_col + 1
        bbox_height = max_row - min_row + 1

        # Convert to YOLO format (normalized)
        center_x = (bbox_x + bbox_width / 2.0) / img_width
        center_y = (bbox_y + bbox_height / 2.0) / img_height
        norm_width = bbox_width / img_width
        norm_height = bbox_height / img_height

        return (center_x, center_y, norm_width, norm_height)

    def create_yolo_annotation(
        self,
        frame_index: int,
        object_results: List[Dict[str, Any]],
        object_id_to_class: Dict[int, int],
    ) -> str:
        """Create YOLO format annotation for a frame."""
        lines = []

        for obj in object_results:
            object_id = obj['object_id']
            rle_mask = obj['mask']

            class_id = object_id_to_class.get(object_id, 0)
            center_x, center_y, width, height = self.mask_to_bbox(rle_mask)

            if width == 0 or height == 0:
                continue

            line = f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}"
            lines.append(line)

        return "\n".join(lines)

    def create_zip_in_memory(
        self,
        session_id: str,
        video_path: str,
        tracking_results: Dict[int, List[Dict[str, Any]]],
        extract_frames: bool = False,
    ) -> io.BytesIO:
        """Create ZIP file in memory."""
        zip_buffer = io.BytesIO()

        # Extract unique object IDs
        all_object_ids = set()
        for frame_results in tracking_results.values():
            for obj in frame_results:
                all_object_ids.add(obj['object_id'])

        sorted_object_ids = sorted(list(all_object_ids))
        object_id_to_class = {obj_id: idx for idx, obj_id in enumerate(sorted_object_ids)}

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add classes.txt
            classes_content = "\n".join([f"object_{obj_id}" for obj_id in sorted_object_ids])
            zipf.writestr(f"session_{session_id}/classes.txt", classes_content)

            # Add annotations
            for frame_index, frame_results in tracking_results.items():
                annotation = self.create_yolo_annotation(
                    frame_index, frame_results, object_id_to_class
                )
                zipf.writestr(
                    f"session_{session_id}/labels/frame_{frame_index:04d}.txt",
                    annotation
                )

            # Add metadata
            metadata = {
                "session_id": session_id,
                "video_path": video_path,
                "num_frames": len(tracking_results),
                "num_objects": len(all_object_ids),
                "object_mapping": {f"object_{obj_id}": class_id
                                 for obj_id, class_id in object_id_to_class.items()},
                "frames": sorted(list(tracking_results.keys())),
            }
            zipf.writestr(
                f"session_{session_id}/metadata.json",
                json.dumps(metadata, indent=2)
            )

            # Extract frames if requested
            if extract_frames and os.path.exists(video_path):
                self._add_frames_to_zip(zipf, video_path, tracking_results.keys(), session_id)

        zip_buffer.seek(0)
        return zip_buffer

    def _add_frames_to_zip(
        self,
        zipf: zipfile.ZipFile,
        video_path: str,
        frame_indices: List[int],
        session_id: str,
    ) -> None:
        """Add frames to ZIP file."""
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            logger.warning(f"Could not open video: {video_path}")
            return

        frame_indices_set = set(frame_indices)
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx in frame_indices_set:
                _, buffer = cv2.imencode('.jpg', frame)
                zipf.writestr(
                    f"session_{session_id}/images/frame_{frame_idx:04d}.jpg",
                    buffer.tobytes()
                )

            frame_idx += 1

        cap.release()
