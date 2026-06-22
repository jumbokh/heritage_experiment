param(
    [string]$PythonExe = ""
)

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not $PythonExe) {
    $PythonExe = "C:\Users\jumbo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
}

& $PythonExe "$ProjectRoot\scripts\preprocess\preprocess_and_inventory.py"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $PythonExe "$ProjectRoot\scripts\detection\import_real_yolo_samples.py"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $PythonExe "$ProjectRoot\scripts\assemble_mixed_detection_dataset.py" --clean
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Output "Real-to-mixed import pipeline completed."
