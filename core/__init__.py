from envcfg.json.solar import DEBUG

from jupiter.stubs.sms_client import install_stub


if DEBUG:
    install_stub()
