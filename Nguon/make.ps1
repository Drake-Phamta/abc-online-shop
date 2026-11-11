# usage: make.ps1 [-Root <07_Tieu_luan folder>] [-Name <file name without extension>]
# build docx -> Word (in a background job: Word COM hangs when driven from this host directly):
# update TOC, save docx, export PDF -> page sheet + free space per page. Word works in C:\a3cap\tieuluan_out
# (plain ASCII path); a successful build is then copied to <Root>\Bai_nop.
param([string]$Root = (Split-Path $PSScriptRoot -Parent), [string]$Name = "tieuluan_V4_04_10_phamtuananh_018")
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$out = "C:\a3cap\tieuluan_out"
New-Item -ItemType Directory -Path $out -Force | Out-Null
$name = $Name
$docx = Join-Path $out "$name.docx"
$pdf = Join-Path $out "$name.pdf"
$started = Get-Date
python (Join-Path $Root "Nguon\build_tieuluan.py") $Root $docx
if ($LASTEXITCODE -ne 0) { "BUILD FAILED"; exit 1 }
$job = Start-Job -ScriptBlock {
    param($docx, $pdf)
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    try {
        $doc = $word.Documents.Open($docx, $false, $false, $false)
        if ($doc.TablesOfContents.Count -ge 1) { $doc.TablesOfContents.Item(1).Update() }
        $doc.Save()
        # ExportAsFixedFormat2 with OptimizeForImageQuality keeps the diagrams at full resolution (the older call
        # lowers every picture above about 220 ppi to 200 ppi, and the small text of large diagrams blurs on zoom)
        try { $doc.ExportAsFixedFormat2($pdf, 17, $false, 0, 0, 1, 1, 0, $true, $true, 1, $true, $true, $false, $true); "pdf: full image quality" }
        catch { $doc.ExportAsFixedFormat($pdf, 17, $false, 0, 0, 1, 1, 0, $true); "pdf: standard export ($_)" }
        "pages: " + $doc.ComputeStatistics(2)
        $doc.Close($false)
    } catch { "WORD ERROR: $_" } finally { $word.Quit() }
} -ArgumentList $docx, $pdf
if (-not (Wait-Job $job -Timeout 240)) { "WORD TIMEOUT"; Stop-Job $job }
$result = Receive-Job $job
Remove-Job $job -Force
$result
python C:\a3cap\toolkit\report\pages.py $pdf (Join-Path $out "_pages.png") | Out-Null
python C:\a3cap\toolkit\report\free.py $pdf
if (($result -match "^pages: ") -and (Test-Path $pdf) -and ((Get-Item $pdf).LastWriteTime -gt $started)) {
    $dest = Join-Path $Root "Bai_nop"
    Copy-Item $docx, $pdf $dest -Force
    "copied to Bai_nop: $name.docx, $name.pdf"
} else { "NOT copied to Bai_nop (build incomplete)" }
