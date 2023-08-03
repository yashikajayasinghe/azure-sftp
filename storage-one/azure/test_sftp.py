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

    hostname = sftp_conn.azure_storage_account+".blob.core.windows.net"
    username = storage_acc_name+"."+local_user_name

    yield {"hostname": hostname, "user_name": username, "pwd": new_pwd}
    sftp_conn.disable_sftp()
    sftp_conn.delete_container()
    sftp_conn.delete_local_user()


@pytest.fixture(scope="module")
def create_service_bus_queue():
    # Create a Service Bus client

    sb_mgmt_client = ServiceBusManagementClient(credential=DefaultAzureCredential(
    ), subscription_id=AZURE_SUBSCRIPTION_ID)
    sb_queue = sb_mgmt_client.queues.create_or_update(
        AZURE_RG_NAME, "sasftp-sb-ns", sb_queue_name, parameters={})
    yield sb_queue

    sb_mgmt_client.queues.delete(AZURE_RG_NAME, "sasftp-sb-ns", sb_queue_name)


@pytest.fixture(scope="module")
def create_event_subscription_for_storage_blob_create_event(create_service_bus_queue):
    # Create an Event Grid client

    eg_topic_name = "sasftp-eventgrid-topic"
    event_subscription_name = "sasftpeventgridsub12342"

    storage_account_resource_id = "/subscriptions/"+AZURE_SUBSCRIPTION_ID + \
        "/resourceGroups/"+AZURE_RG_NAME + \
        "/providers/Microsoft.Storage/storageAccounts/sasftp02"
    print(f"azzure sub id is {AZURE_SUBSCRIPTION_ID}")
    eg_mgmt_client = EventGridManagementClient(credential=DefaultAzureCredential(
    ), subscription_id=AZURE_SUBSCRIPTION_ID)
    
    destination = ServiceBusQueueEventSubscriptionDestination(
        resource_id=create_service_bus_queue.id)
    filter = EventSubscriptionFilter(
        included_event_types=["Microsoft.Storage.BlobCreated"],
        is_subject_case_sensitive=False,
        subject_begins_with="/blobServices/default/containers/sftpcont",
        subject_ends_with=".txt"
    )
    event_subscription_info = EventSubscription(
        destination=destination, filter=filter)
    event_subscription_async_poller = eg_mgmt_client.event_subscriptions.begin_create_or_update(
        storage_account_resource_id,
        event_subscription_name,
        event_subscription_info
    )  

    event_subscription = event_subscription_async_poller.result()
    assert event_subscription.provisioning_state == "Succeeded"
    
    yield event_subscription

    # Delete the event subscription
    print("deleting event subscription "+event_subscription_name)
    eg_mgmt_client.event_subscriptions.begin_delete(scope=storage_account_resource_id, event_subscription_name=event_subscription_name)
    
@pytest.fixture(scope="module")
def create_dir_in_sftp_storage(setup_sftp):

    hos = setup_sftp["hostname"]
    user = setup_sftp["user_name"]
    pwd = setup_sftp["pwd"]
    # cont_name = setup_sftp["storage_cont_name"]
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
        sftp.mkdir('out')
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

def test_upload_file(setup_sftp, create_dir_in_sftp_storage, create_service_bus_queue: ServiceBusManagementClient, create_event_subscription_for_storage_blob_create_event):
    # Create an SSH client
    sftp_connection_info = setup_sftp
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    print("Connecting to SFTP server "+sftp_connection_info["hostname"])
    time.sleep(10)
    ssh.connect(hostname=sftp_connection_info["hostname"],
                username=sftp_connection_info["user_name"], password=sftp_connection_info["pwd"], timeout=20)

    # Open an SFTP session
    sftp = ssh.open_sftp()

    # Perform SFTP operations
    local_file_path = 'file.txt'
    remote_file_path = 'directdebit/out/file.txt'
    sftp.put(local_file_path, remote_file_path)

    # Close the SFTP session and SSH connection
    sftp.close()
    ssh.close()

    time.sleep(10)

    #  receive message payload for the blob create event from the sb queue
    with ServiceBusClient(sb_hostname, DefaultAzureCredential()) as sb_client:
        with sb_client.get_queue_receiver(sb_queue_name, max_wait_time=30) as receiver:
            for msg in receiver:
                print("Received: " + str(msg))
                

    print("Test Completed")
    
    assert True
