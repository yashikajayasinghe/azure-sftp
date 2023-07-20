terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}
provider "azurerm" {
  features {}

  subscription_id = var.AZURE_SUBSCRIPTION_ID
  tenant_id       = "bce8dd2e-d150-45ed-95fc-3ab94970431d"

}

resource "azurerm_resource_group" "sftp_rg" {
  name     = "rg-terraform-sftp-storage_2"
  location = "East Us"
  tags = {
    environment = "dev"
  }
}
# module "storage_account" {
#   source  = "claranet/storage-account/azurerm"
#   version = "~> 7.5.0"

#   storage_account_custom_name = "sasftpdtestrig"
#   environment                 = azurerm_resource_group.rg.tags.environment
#   location                    = "East Us"
#   location_short              = "eastus"
#   logs_destinations_ids       = []
#   resource_group_name         = azurerm_resource_group.rg.name
#   sftp_enabled                = false
#   account_tier                = "Standard"
#   account_replication_type    = "LRS"
#   min_tls_version             = "TLS1_2"
#   stack                       = ""
#   client_name                 = ""

# }

resource "azurerm_storage_account" "sasftptestrig2" {
  name                     = "sasftptestrig2"
  resource_group_name      = azurerm_resource_group.sftp_rg.name
  location                 = azurerm_resource_group.sftp_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"
  is_hns_enabled           = true
  sftp_enabled             = false
  tags = {
    environment = "dev"
  }
}


