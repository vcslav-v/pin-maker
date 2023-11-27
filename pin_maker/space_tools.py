from boto3 import session as s3_session
from pin_maker.config import DO_SPACE_BUCKET, DO_SPACE_REGION, DO_SPACE_ENDPOINT, DO_SPACE_KEY, DO_SPACE_SECRET


def get_s3_link(key):
    do_session = s3_session.Session()
    client = do_session.client(
        's3',
        region_name=DO_SPACE_REGION,
        endpoint_url=DO_SPACE_ENDPOINT,
        aws_access_key_id=DO_SPACE_KEY,
        aws_secret_access_key=DO_SPACE_SECRET
    )
    return client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': DO_SPACE_BUCKET,
            'Key': key,
        },
        ExpiresIn=15000
    )


def save_to_space(data: str, template_name: str, pin_file_name: str) -> str:
    do_session = s3_session.Session()
    client = do_session.client(
        's3',
        region_name=DO_SPACE_REGION,
        endpoint_url=DO_SPACE_ENDPOINT,
        aws_access_key_id=DO_SPACE_KEY,
        aws_secret_access_key=DO_SPACE_SECRET
    )
    key = f'{template_name}/{pin_file_name}'
    client.put_object(
        Bucket=DO_SPACE_BUCKET,
        Body=data,
        Key=key,
        ACL='public-read',
        StorageClass='REDUCED_REDUNDANCY',
        ContentType='application/octet-stream',
    )
    return key
