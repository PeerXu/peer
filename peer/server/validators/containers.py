from eve.io.mongo import Validator

class ContainerValidator(Validator):
    def _validate_is_container_status_updatable(self, is_container_status_updatable, field, value):
        pass

VALIDATORS = [ContainerValidator]
