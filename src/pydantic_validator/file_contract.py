from pydantic import BaseModel, validator
import re

class Meta(BaseModel):
    filename: str
    mime_type: str
    content: str

    @validator("filename")
    def validate_filename(cls, value):
        pattern = r"^meta_(0[1-9]|1[0-2])_\d{4}\.csv$"
        if not re.match(pattern, value):
            raise ValueError("Filename must match 'meta_MM_YYYY.csv' format")
        return value

    @validator("mime_type")
    def validate_mime_type(cls, value):
        if value not in ["text/csv", "application/vnd.ms-excel"]:
            raise ValueError("File must be a CSV")
        return value

    @validator("content")
    def validate_content(cls, value):
        lines = value.strip().splitlines()
        if not lines:
            raise ValueError("CSV file is empty")

        # Validate header
        header = lines[0].strip().lower()
        if header != "vendedor;valor":
            raise ValueError("CSV header must be exactly 'vendedor;valor'")

        # Validate each row
        for idx, line in enumerate(lines[1:], start=2):
            parts = line.split(";")
            if len(parts) != 2:
                raise ValueError(f"Line {idx} must have exactly 2 columns separated by ';'")
            vendedor, valor = parts
            if not vendedor.strip():
                raise ValueError(f"Line {idx}: 'vendedor' cannot be empty")
            if not valor.strip().isdigit():
                raise ValueError(f"Line {idx}: 'valor' must be a number")
        return value
