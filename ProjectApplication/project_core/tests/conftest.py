import pytest
from botocore.stub import Stubber

from app.aws import s3_resource


@pytest.fixture(autouse=True)
def s3_stub():
    with Stubber(s3.meta.client) as stubber:
        yield stubber
        stubber.assert_no_pending_responses()