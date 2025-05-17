[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Ruta al DLL de OpenHardwareMonitor
$dllPath = "C:\Proyectos Universidad\Sistemas Operacionales\sysguardian_ai\herramientas\OpenHardwareMonitorLib.dll"

# Desbloquear el archivo DLL si es necesario
Unblock-File -Path $dllPath

# Cargar el ensamblado
Add-Type -Path $dllPath

# Crear una instancia del objeto Computer
$computer = New-Object OpenHardwareMonitor.Hardware.Computer
$computer.CPUEnabled = $true
$computer.Open()

# Actualizar los datos de hardware
foreach ($hardware in $computer.Hardware) {
    $hardware.Update()
    if ($hardware.HardwareType -eq "CPU") {
        foreach ($sensor in $hardware.Sensors) {
        if ($sensor.SensorType -eq "Temperature" -and $sensor.Name -like "*Core*" -and $sensor.Value -ne $null) {
            $temp = "$($sensor.Name): $($sensor.Value) C"
            Write-Output $temp
        }

        }
    }
}

$computer.Close()
