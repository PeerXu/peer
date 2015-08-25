import re
from eve.io.mongo import Validator

class SHA1Validator(Validator):
    REGEX = re.compile('^[0-9a-f]{40}$')
    def _validate_type_sha1(self, field, value):
        if not self.REGEX.match(value):
            self._error(field, "value '%s' cannot converted to a sha1" % value)

VALIDATORS = [SHA1Validator]
