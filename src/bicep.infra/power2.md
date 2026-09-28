Run the whole workflow from the directory containing the script and Bicep files:

rg_gtgh_data_13


.\deploy.ps1 `
    -ResourceGroup "rg-instructor-01" `
    -Location "westeurope" `
    -AcrName "dim02accwse12345aa" `
    -EnvironmentName "dimmer-env" `
    -ContainerAppName "dimmer"




cleanup.ps1 is a PowerShell file containing the delete commands.



.\cleanup.ps1 -ResourceGroup "rg-instructor-01"