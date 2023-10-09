from sasftp import SaSftp
import os, sys
import paramiko
import time
import uuid
import pytest
from azure.servicebus.management import ServiceBusAdministrationClient
from azure.mgmt.servicebus import ServiceBusManagementClient
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.identity import DefaultAzureCredential
from azure.mgmt.eventgrid import EventGridManagementClient
from azure.mgmt.eventgrid.models import (EventSubscription,
                                         EventSubscriptionFilter,
                                         ServiceBusQueueEventSubscriptionDestination,
                                         StringContainsAdvancedFilter,
                                         Topic
                                         )

# getattr(os.environ, "AZURE_SUBSCRIPTION_ID", None)
AZURE_SUBSCRIPTION_ID = os.getenv('AZURE_SUBSCRIPTION_ID') 
AZURE_RESOURCE_GROUP_NAME = "rg-terraform-sftp-storage_2"
AZURE_RG_NAME = "rg-terraform-sftp-storage_2"
sb_queue_name = "sbq-"+str(uuid.uuid4())
sb_hostname = "sasftp-sb-ns.servicebus.windows.net"


@pytest.fixture(scope="module")
def setup_sftp():  # input request fixture

    # subscription_id = getattr(os.environ, "AZURE_SUBSCRIPTION_ID", None)
    # resource_group_name = getattr(os.environ, "AZURE_RESOURCE_GROUP_NAME", "rg-terraform-sftp-storage_2")
    storage_acc_name = getattr(
        os.environ, "AZURE_STORAGE_ACCOUNT_NAME", "sasftp02")
    storage_cont_name = getattr(
        os.environ, "AZURE_STORAGE_CONTAINER_NAME", "sftpcont"+str(uuid.uuid4()))
    local_user_name = getattr(
        os.environ, "AZURE_LOCAL_USER_NAME", "user"+str(int(time.time())))

    sftp_conn = SaSftp(subscription_id=AZURE_SUBSCRIPTION_ID,
                       resource_group_name=AZURE_RG_NAME,
                       storage_acc_name=storage_acc_name,
                       storage_cont_name=storage_cont_name,
                       local_user_name=local_user_name)

    sftp_conn.enable_sftp()
    sftp_conn.create_container()
    sftp_conn.create_local_user()
    new_pwd = sftp_conn.regenerate_password()
    time.sleep(5)

    hostname = sftp_conn.azure_storage_account+".blob.core.windows.net"
    username = storage_acc_name+"."+local_user_name
    
    yield {"hostname": hostname, "user_name": username, "pwd": new_pwd, "storage_cont_name": storage_cont_name}
    sftp_conn.disable_sftp()
    sftp_conn.delete_container()
    sftp_conn.delete_local_user()

@pytest.fixture(scope="module")
def create_dir_in_sftp_storage(setup_sftp):

    hos = setup_sftp["hostname"]
    user = setup_sftp["user_name"]
    pwd = setup_sftp["pwd"]
    cont_name = setup_sftp["storage_cont_name"]
    sftp = None

    try:
        transport = paramiko.Transport((hos, 22))
        transport.connect(username=user, password=pwd)
        sftp = paramiko.SFTPClient.from_transport(transport)

        # Create a directory in the remote storage
        remote_path = '/'
        sftp.chdir(remote_path)
        sftp.mkdir('directdebit')
        sftp.chdir('directdebit')
        sftp.mkdir('inbound')
    except paramiko.AuthenticationException as e:
        print("Authentication failed:", str(e))
    except paramiko.SSHException as e:
        print("SSH error:", str(e))
    except paramiko.sftp.SFTPError as e:
        print("SFTP error:", str(e))
    except FileNotFoundError as e:
        print("File not found:", str(e))
    except Exception as e:
        print("Error:", str(e))
    finally:
        if sftp is not None:
            print("Closing SFTP connection")
            sftp.close()
        if transport:
            print("Closing Transport connection")
            transport.close()



def test_mkdir_ssh(create_dir_in_sftp_storage):
    time.sleep(60)
    pass
