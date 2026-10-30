from storage import AssetStorage
from tests.conftest import S3_BUCKET as BUCKET
from tests.conftest import S3_ENV as ENV
from tests.conftest import S3_PREFIX, object_key


def test_upload_stores_public_object_under_the_env_prefix(s3):
    storage = AssetStorage.from_env(ENV)
    assert storage is not None

    url = storage.upload("partners/7/logo.png", b"png-bytes", "image/png")

    assert url == f"{ENV['S3_PUBLIC_BASE_URL']}/{object_key('partners/7/logo.png')}"
    stored = s3.get_object(Bucket=BUCKET, Key=object_key("partners/7/logo.png"))
    assert stored["Body"].read() == b"png-bytes"
    assert stored["ContentType"] == "image/png"


def test_delete_removes_the_prefixed_object(s3):
    storage = AssetStorage.from_env(ENV)
    assert storage is not None
    storage.upload("partners/3/logo.jpg", b"jpg-bytes", "image/jpeg")

    storage.delete("partners/3/logo.jpg")

    assert "Contents" not in s3.list_objects_v2(Bucket=BUCKET)


def test_expire_prefix_is_scoped_to_the_env_and_kept_when_applied_twice(s3):
    storage = AssetStorage.from_env(ENV)
    assert storage is not None
    storage.expire_prefix("tmp/", days=1)
    storage.expire_prefix("tmp/", days=1)

    rules = s3.get_bucket_lifecycle_configuration(Bucket=BUCKET)["Rules"]
    assert len(rules) == 1
    assert rules[0]["Filter"]["Prefix"] == f"{S3_PREFIX}/tmp/"
    assert rules[0]["Expiration"]["Days"] == 1


def test_public_url_uses_the_cdn_host_and_prefix():
    storage = AssetStorage.from_env({**ENV, "S3_PUBLIC_BASE_URL": "https://cdn.mikebaliai.com/"})
    assert storage is not None
    assert (
        storage.public_url("partners/1/logo.png")
        == "https://cdn.mikebaliai.com/test/partners/1/logo.png"
    )


def test_storage_stays_off_when_the_prefix_is_missing():
    values = {key: value for key, value in ENV.items() if key != "S3_KEY_PREFIX"}
    assert AssetStorage.from_env(values) is None
