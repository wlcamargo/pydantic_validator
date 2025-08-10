import streamlit as st
import boto3
from botocore.client import Config
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
from file_contract import Meta

from dotenv import load_dotenv
import os

st.set_page_config(page_title="Import Targets", layout="wide")
st.title("Import Targets")

# Load environment variables from .env file
load_dotenv()

# S3 variables
s3_endpoint = os.getenv("S3_ENDPOINT")
s3_access_key = os.getenv("S3_ACCESS_KEY")
s3_secret_key = os.getenv("S3_SECRET_KEY")
bucket_name = os.getenv("BUCKET_NAME")

# Initialize S3 client for MinIO
s3 = boto3.client(
    "s3",
    endpoint_url=s3_endpoint,
    aws_access_key_id=s3_access_key,
    aws_secret_access_key=s3_secret_key,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1"
)
        
st.subheader("📤 Upload File to S3")

uploaded_file = st.file_uploader("Choose a file to upload", type=None)

if uploaded_file is not None:
    st.write(f"Selected file: `{uploaded_file.name}`")

    if st.button("Upload to MinIO"):
        try:
            file_content = uploaded_file.read().decode("utf-8")

            # Valida contrato
            Meta(
                filename=uploaded_file.name,
                mime_type=uploaded_file.type,
                content=file_content
            )

            uploaded_file.seek(0)

            s3.upload_fileobj(
                Fileobj=uploaded_file,
                Bucket=bucket_name,
                Key=uploaded_file.name
            )
            st.success(f"✅ File `{uploaded_file.name}` successfully uploaded to bucket.")
        except Exception as e:
            st.error(f"❌ Validation or upload error: {e}")
            

st.subheader("📁 S3 File Explorer")
try:
    response = s3.list_objects_v2(Bucket=bucket_name)

    if "Contents" in response:
        files = response["Contents"]
        st.markdown(f"📦 Total files: **{len(files)}**")

        # Table headers
        col1, col2, col3, col4 = st.columns([4, 3, 2, 2])
        col1.markdown("**📄 File Name**")
        col2.markdown("**🕒 Last Modified**")
        col3.markdown("**📦 Size (KB)**")
        col4.markdown("**📥 Download**")

        for obj in files:
            key = obj["Key"]
            last_modified = obj["LastModified"].strftime("%Y-%m-%d %H:%M:%S")
            size_kb = round(obj["Size"] / 1024, 2)

            # Read file content from MinIO (in-memory)
            file_obj = s3.get_object(Bucket=bucket_name, Key=key)
            file_bytes = file_obj["Body"].read()

            # Table row
            col1, col2, col3, col4 = st.columns([4, 3, 2, 2])
            col1.markdown(f"`{key}`")
            col2.markdown(last_modified)
            col3.markdown(f"{size_kb} KB")

            # Streamlit download button
            col4.download_button(
                label="⬇️ Download",
                data=file_bytes,
                file_name=key,
                mime="application/octet-stream",
                key=key  # important to avoid conflicts between buttons
            )

    else:
        st.info("No files found in the bucket.")

except Exception as e:
    st.error(f"❌ Error while listing files: {e}")

