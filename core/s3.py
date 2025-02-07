from config import app_logger, boto3_session, settings


async def upload_to_s3(file_contents, filename):
    app_logger.info(f"Uploading {filename} to S3")
    async with boto3_session.client("s3") as client:
        await client.put_object(
            Bucket=settings.s3_bucket_name, Key=filename, Body=file_contents
        )
        url = f"https://{settings.s3_bucket_name}.s3.{settings.aws_region}.amazonaws.com/{filename}"
    return url
