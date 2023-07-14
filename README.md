# azure-sftp
Azure Python SDK - SFTP Blob Storage

Steps:
1. Provision a Azure Storage account with Terraform
2. Via Azure CLI commands:
   1. Enable SFTP
   2. create a container
   3. create a local user with rwldc permissions for the containr
3. using Python sftp client library `paramiko` do a ssh file transfer to the container
4. Via Azure CLI:
   1. delete local use
   2. delete container
   3. disable SFTP

# Ref

1. https://learn.microsoft.com/en-us/azure/developer/terraform/get-started-cloud-shell-bash?tabs=bash
2. https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_account#sftp_enabled
3. https://learn.microsoft.com/en-us/azure/storage/blobs/secure-file-transfer-protocol-support
4. https://learn.microsoft.com/en-us/python/api/azure-storage-blob/azure.storage.blob.containerclient?view=azure-python
5. https://azure.github.io/azure-sdk/releases/latest/index.html#python
6. https://learn.microsoft.com/en-us/cli/azure/storage?view=azure-cli-latest
7. https://dev.to/manukanne/tutorial-create-an-azure-blob-storage-with-sftp-integration-cd6
8. https://www.jorgebernhardt.com/azure-storage-blobs-enable-sftp-support/ 

