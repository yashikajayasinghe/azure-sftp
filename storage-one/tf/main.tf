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

resource "azurerm_storage_account" "sasftp" {
  name                     = "sasftp02"
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

resource "azurerm_servicebus_namespace" "sevicebus_namespace" {
  name                = "sasftp-sb-ns"
  resource_group_name = azurerm_resource_group.sftp_rg.name
  location            = azurerm_resource_group.sftp_rg.location
  sku                 = "Standard"

  tags = {
    environment = "dev"
  }
}

# resource "azurerm_eventgrid_topic" "eventgrid_topic" {
#   name                = "sasftp-eventgrid-topic"
#   resource_group_name = azurerm_resource_group.sftp_rg.name
#   location            = azurerm_resource_group.sftp_rg.location
#   input_schema        = "CloudEventSchemaV1_0"

#   tags = {
#     environment = "dev"
#   }
# }




