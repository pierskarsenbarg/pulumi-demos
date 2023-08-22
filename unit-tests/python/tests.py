import unittest
import pulumi
from pulumi_azure_native import storage

class MyMocks(pulumi.runtime.Mocks):
    def new_resource(self, args: pulumi.runtime.MockResourceArgs):
        outputs = args.inputs
        if args.typ == "azure-native:storage:StorageAccount":
            outputs = {
                **args.inputs
            }
        return [args.name + '_id', args.inputs]
    def call(self, args: pulumi.runtime.MockCallArgs):
        return {}

pulumi.runtime.set_mocks(
    MyMocks(),
    preview=False, 
)

import infra

class Tests(unittest.TestCase):

    @pulumi.runtime.test
    def test_storage_account(self):
        def check_kind(args):
            urn, kind = args
            self.assertEqual(kind, storage.Kind.STORAGE_V2, f'storage account {urn} should be of kind STORAGE_V2')

        return pulumi.Output.all(infra.account.urn, infra.account.kind).apply(check_kind)
    
    @pulumi.runtime.test
    def test_blob_container(self):
        def check_public_access(args):
            urn, public_access = args
            self.assertEqual(public_access, storage.PublicAccess.NONE, f'blob container {urn} should have public access set to NONE')
        
        return pulumi.Output.all(infra.blob_container.urn, infra.blob_container.public_access).apply(check_public_access)