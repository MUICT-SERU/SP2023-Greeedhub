from applauncher.kernel import Kernel, Environments, KernelReadyEvent
import mongoengine_bundle
import inject
from mongoengine import fields, Document

class Dog(Document):
    name = fields.StringField()

class MyBundle(object):
    def __init__(self):
        self.event_listeners = [
            (KernelReadyEvent, self.kernel_ready)
        ]
        
    def kernel_ready(self, event):
        Dog(name="perro").save()
        print("DOG SAVED :)")

bundle_list = [
    mongoengine_bundle.MongoEngineBundle(),
    MyBundle()
]
with Kernel(Environments.PRODUCTION, bundle_list) as kernel:
    kernel.wait()
