import sys
import boto3
import datetime
import pytz

BUCKET = 'openstates-backups'


def cleanup(older_than):
    older_than = datetime.datetime.strptime(older_than, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    assert now - older_than > datetime.timedelta(days=30)

    s3 = boto3.client('s3')

    for obj in s3.list_objects_v2(Bucket=BUCKET)['Contents']:
        if obj['LastModified'] < older_than:
            print(f'delete {obj["Key"]}')
            s3.delete_object(Bucket=BUCKET, Key=obj['Key'])


if __name__ == '__main__':
    cleanup(sys.argv[1])
