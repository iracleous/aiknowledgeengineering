
dim02accwse12345  Container registry  Germany West Central
dimmer            Container App       Germany West Central
dimmer-env        Container Apps Environment  Germany West Central
workspace-rginstructor013gDD  Log Analytics workspace Germany West Central







powershell variables
```
$ResourceGroup = "rg-instructor-01"
$Location = " germanywestcentral"

# Must be globally unique and lowercase.
$AcrName = "dim02accwse12345"

$EnvironmentName = "dimmer-env"
$IdentityName = "dimmer-acr-pull"
$ContainerAppName = "dimmer"

$LocalImage = "fastapi-app-dim:0.1"
$ImageName = "fastapi-app-dim"
$ImageTag = "0.1"


```


Step 2 commands
```
#Creates ACR
az acr create `
  --resource-group $ResourceGroup `
  --name $AcrName `
  --sku Basic `
  --admin-enabled true

#Logs to ACR
az acr login --name $AcrName

#Gets the login for ACR
$LoginServer = az acr show `
  --name $AcrName `
  --query loginServer `
  --output tsv

#changes the tag of the 
docker tag fastapi-app-dim:0.1 "${LoginServer}/$LocalImage"

docker push "${LoginServer}/$LocalImage"



az containerapp env create `
  --name $EnvironmentName `
  --resource-group $ResourceGroup `
  --location $Location

az acr update -n $AcrName --admin-enabled true


$AcrUsername = az acr credential show `
  --name $AcrName `
  --query username `
  --output tsv

$AcrPassword = az acr credential show `
  --name $AcrName `
  --query "passwords[0].value" `
  --output tsv

az containerapp create `
  --name $ContainerAppName `
  --resource-group $ResourceGroup `
  --environment $EnvironmentName `
  --image "${LoginServer}/$LocalImage" `
  --registry-server $LoginServer `
  --registry-username $AcrUsername `
  --registry-password $AcrPassword `
  --ingress external `
  --target-port 8000 `
  --min-replicas 0 `
  --max-replicas 1


$Fqdn = az containerapp show `
  --name $ContainerAppName `
  --resource-group $ResourceGroup `
  --query "properties.configuration.ingress.fqdn" `
  --output tsv


```

when api key is available

```
# Set this locally before running the deployment command.
$ApiKey = "replace-with-a-long-random-secret"

az containerapp create `
  --name $ContainerAppName `
  --resource-group $ResourceGroup `
  --environment $EnvironmentName `
  --image "${LoginServer}/$LocalImage" `
  --registry-server $LoginServer `
  --registry-username $AcrUsername `
  --registry-password $AcrPassword `
  --ingress external `
  --target-port 8000 `
  --min-replicas 0 `
  --max-replicas 1 `
  --secrets "incidents-api-key=$ApiKey" `
  --env-vars "INCIDENTS_API_KEY=secretref:incidents-api-key"

```


$WorkspaceName = "law-incidents"


# 1. Create the Log Analytics workspace
az monitor log-analytics workspace create `
  --resource-group $ResourceGroup `
  --workspace-name $WorkspaceName `
  --location $Location

# 2. Get its workspace ID and shared key
$WorkspaceId = az monitor log-analytics workspace show `
  --resource-group $ResourceGroup `
  --workspace-name $WorkspaceName `
  --query customerId `
  --output tsv

$WorkspaceKey = az monitor log-analytics workspace get-shared-keys `
  --resource-group $ResourceGroup `
  --workspace-name $WorkspaceName `
  --query primarySharedKey `
  --output tsv

# 3. Create the Container Apps environment connected to it
az containerapp env create `
  --name $EnvironmentName `
  --resource-group $ResourceGroup `
  --location $Location `
  --logs-destination log-analytics `
  --logs-workspace-id $WorkspaceId `
  --logs-workspace-key $WorkspaceKey