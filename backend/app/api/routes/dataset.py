"""Dataset upload endpoint.

POST /api/dataset/upload — accept a CSV file and run the full pipeline
(validate -> clean -> search_text -> embeddings -> FAISS -> metadata save),
returning the processing status, record count, and index status.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.routes.auth import get_current_user
from app.core.logger import get_logger
from app.models.schemas import DatasetUploadResponse
from app.services.dataset_service import (
    DatasetValidationError,
    IndexingError,
    InvalidCSVError,
    process_upload,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/dataset", tags=["dataset"])

_MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB guard


@router.post(
    "/upload",
    response_model=DatasetUploadResponse,
    summary="Upload a CSV and rebuild the incident index",
)
def upload_dataset(
    file: UploadFile = File(...),
    _user: dict = Depends(get_current_user),
) -> DatasetUploadResponse:
    """Validate, clean, embed, and index an uploaded incidents CSV (auth required)."""
    filename = file.filename or "upload"
    if not filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload a .csv file.",
        )

    try:
        contents = file.file.read()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to read uploaded file: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not read the uploaded file.",
        ) from exc
    finally:
        file.file.close()

    if len(contents) > _MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Uploaded file exceeds the 50 MB limit.",
        )

    logger.info("Received upload '%s' (%d bytes)", filename, len(contents))

    try:
        return process_upload(contents)
    except InvalidCSVError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except DatasetValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Dataset validation failed.", "errors": exc.errors},
        ) from exc
    except IndexingError as exc:
        # Generic message; the real cause is logged server-side only.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    except Exception as exc:  # noqa: BLE001 - last-resort guard
        logger.exception("Unexpected error during dataset upload")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error while processing the dataset.",
        ) from exc
