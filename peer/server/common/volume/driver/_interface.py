class VolumeDriverInterface(object):
    def create(self, volume):
        pass

    def delete(self, volume):
        pass

    def mount(self, agent, volumes):
        pass
