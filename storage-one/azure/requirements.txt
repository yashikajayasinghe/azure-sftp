data "azurerm_storage_account" "example" {
  name                = "packerimages"
  resource_group_name = "packer-storage"
}

output "storage_account_tier" {
  value = data.azurerm_storage_account.example.account_tier
}