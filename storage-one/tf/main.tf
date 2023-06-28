terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=3.0.0"
    }
  }
}
provider "azurerm" {
  features {}

  subscription_id = "27d13b5e-2698-472d-a869-93da20c061d5"
  tenant_id       = "bce8dd2e-d150-45ed-95fc-3ab94970431d"

}

resource "azurerm_resource_group" "rg" {
  name     = "rg-terraform-sftp-storage"
  location = "East Us"
  tags = {
    environment = "dev"
  }
}

resource "azurerm_storage_account" "storage_ac" {
  name = "sftp-storage-account"
  location = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  
}