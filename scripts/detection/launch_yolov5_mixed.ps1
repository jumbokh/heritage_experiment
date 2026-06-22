param(
    [string]$PythonExe = "",
    [string]$Weights = "yolov5n.pt",
    [int]$ImgSize = 960,
    [int]$Batch = 8,
    [int]$Epochs = 100,
    [string]$Device = "cpu",
    [int]$Workers = 4,
    [switch]$Execute
)

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not $PythonExe) {
    $PythonExe = "$ProjectRoot\.venv-yolov5\Scripts\python.exe"
}

$argsList = @(
    "$ProjectRoot\scripts\detection\train_yolov5.py",
    "--dataset-type", "mixed",
    "--python", $PythonExe,
    "--weights", $Weights,
    "--imgsz", $ImgSize,
    "--batch", $Batch,
    "--epochs", $Epochs,
    "--device", $Device,
    "--workers", $Workers
)

if ($Execute) {
    $argsList += "--execute"
}

& $PythonExe $argsList
