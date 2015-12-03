import re
from eve.io.mongo import Validator

class SHA256Validator(Validator):
    REGEX = re.compile('^[0-9a-f]{64}$')
    def _validate_type_sha256(self, field, value):
        if not self.REGEX.match(value):
            self._error(field, "value '%s' cannot converted to a sha256" % value)

VALIDATORS = [SHA256Validator]
