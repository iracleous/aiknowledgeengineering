dim02accwse12345    Container registry
dimmer              Container App
dimmer-env          Container Apps Environment
dimmer-pull         Managed Identity
law-incidents       Log Analytics workspace


clean up


# Set this to the resource group containing the five resources.
$ResourceGroup = "rg-instructor-01"

# Check the resources before deleting them.
az resource list `
  --resource-group $ResourceGroup `
  --query "[?contains(['dim02accwse12345','dimmer','dimmer-env','dimmer-pull','law-incidents'], name)].{Name:name, Type:type}" `
  --output table


  # 1. Delete the app before its environment and pull identity.
az containerapp delete `
  --name dimmer `
  --resource-group $ResourceGroup `
  --yes

# 2. Delete the Container Apps environment.
az containerapp env delete `
  --name dimmer-env `
  --resource-group $ResourceGroup `
  --yes

# 3. Delete the managed identity.
az identity delete `
  --name dimmer-pull `
  --resource-group $ResourceGroup

# 4. Delete the registry.
az acr delete `
  --name dim02accwse12345 `
  --resource-group $ResourceGroup `
  --yes

# 5. Delete the Log Analytics workspace.
az monitor log-analytics workspace delete `
  --workspace-name law-incidents `
  --resource-group $ResourceGroup `
  --yes


  