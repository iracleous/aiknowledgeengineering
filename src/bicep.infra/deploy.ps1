param(
    [Parameter(Mandatory)]
    [string]$ResourceGroup,

    [Parameter(Mandatory)]
    [string]$Location,

    [Parameter(Mandatory)]
    [string]$AcrName,

    [Parameter(Mandatory)]
    [string]$EnvironmentName,

    [Parameter(Mandatory)]
    [string]$ContainerAppName
)

$LocalImage = "fastapi-app-dim:0.1"
$WorkspaceName = "law-incidents"
$ApiKey = Read-Host "Enter the incidents API key"

function Assert-LastCommand {
    if ($LASTEXITCODE -ne 0) {
        throw "The previous command failed with exit code $LASTEXITCODE"
    }
}

az deployment group create `
    --resource-group $ResourceGroup `
    --template-file .\infrastructure.bicep `
    --parameters `
        location=$Location `
        acrName=$AcrName `
        environmentName=$EnvironmentName `
        workspaceName=$WorkspaceName
Assert-LastCommand

# docker build -t $LocalImage .
# Assert-LastCommand

az acr login --name $AcrName
Assert-LastCommand

$LoginServer = az acr show `
    --name $AcrName `
    --query loginServer `
    --output tsv
Assert-LastCommand

docker tag $LocalImage "${LoginServer}/$LocalImage"
Assert-LastCommand

docker push "${LoginServer}/$LocalImage"
Assert-LastCommand

az deployment group create `
    --resource-group $ResourceGroup `
    --template-file .\app.bicep `
    --parameters `
        location=$Location `
        acrName=$AcrName `
        environmentName=$EnvironmentName `
        containerAppName=$ContainerAppName `
        imageName=$LocalImage `
        incidentsApiKey=$ApiKey `
    --query "properties.outputs.url.value" `
    --output tsv
Assert-LastCommand

