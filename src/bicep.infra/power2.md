Run the whole workflow from the directory containing the script and Bicep files:

.\deploy.ps1 `
    -ResourceGroup "your-resource-group" `
    -Location "westeurope" `
    -AcrName "dim02accwse12345" `
    -EnvironmentName "dimmer-env" `
    -ContainerAppName "dimmer"




cleanup.ps1 is a PowerShell file containing the delete commands.



.\cleanup.ps1 -ResourceGroup "your-resource-group-name"