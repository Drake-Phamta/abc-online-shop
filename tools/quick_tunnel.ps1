# Public address for the demo shop through a Cloudflare quick tunnel: https://<random words>.trycloudflare.com forwards
# to http://localhost:8080 on this computer for as long as this window stays open. No Cloudflare account is needed;
# the address changes every time. Anyone who has the address can use the shop with the demo accounts; the data is
# demo data, and CHAY_DEMO.bat recreates it. Started by CHAY_TUNNEL.bat. Keep this file ASCII only (PowerShell 5.1).
$root = Split-Path -Parent $PSScriptRoot
$shop = "http://localhost:8080/"

function Answers { try { Invoke-WebRequest -UseBasicParsing -TimeoutSec 3 $shop | Out-Null; return $true } catch { return $false } }

# 1. cloudflared: on the PATH, or the official binary in %LOCALAPPDATA%\cloudflared (downloaded once from GitHub)
$exe = (Get-Command cloudflared -ErrorAction SilentlyContinue).Source
if (-not $exe) { $exe = Join-Path $env:LOCALAPPDATA "cloudflared\cloudflared.exe" }
if (-not (Test-Path $exe)) {
    Write-Host "Downloading cloudflared from github.com/cloudflare/cloudflared (once) ..."
    New-Item -ItemType Directory -Force (Split-Path $exe) | Out-Null
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -UseBasicParsing "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile $exe
}
if ((Get-AuthenticodeSignature $exe).Status -ne "Valid") { Write-Host "cloudflared.exe is not signed by Cloudflare: stopped."; exit 1 }

# 2. the shop must answer first
if (-not (Answers)) {
    Write-Host "The shop is not running: starting CHAY_DEMO.bat in its own window ..."
    Start-Process -FilePath (Join-Path $root "CHAY_DEMO.bat") -WorkingDirectory $root
    for ($i = 0; $i -lt 120 -and -not (Answers); $i++) { Start-Sleep -Seconds 1 }
    if (-not (Answers)) { Write-Host "The shop did not start; see the window of CHAY_DEMO.bat."; exit 1 }
}

# 3. the tunnel runs in this window; its log gives the public address. If cloudflared stops (network loss), it is
#    started again; every new address is written into the "Website" field of the public GitHub repository, where the
#    published showcase (GitHub Pages) reads it, so its "Open the shop" button always opens the current address.
$repo = "Drake-Phamta/abc-online-shop"
$gh = (Get-Command gh -ErrorAction SilentlyContinue).Source
$log = Join-Path $env:TEMP "abc_shop_tunnel.log"
$first = $true

# The address also goes into live.txt of the branch "live" (not the published branch "main"): the showcase reads it from
# raw.githubusercontent.com when the GitHub API is out of its hourly limit. Commits use the GitHub noreply address.
function Publish-Live([string]$address) {
    $who = "178000393+Drake-Phamta@users.noreply.github.com"
    & $gh api "repos/$repo/branches/live" --silent 2>$null
    if ($LASTEXITCODE -ne 0) {
        $main = & $gh api "repos/$repo/git/ref/heads/main" --jq .object.sha 2>$null
        & $gh api -X POST "repos/$repo/git/refs" -f "ref=refs/heads/live" -f "sha=$main" --silent 2>$null
    }
    $sha = & $gh api "repos/$repo/contents/live.txt?ref=live" --jq .sha 2>$null
    $body = @("-X", "PUT", "repos/$repo/contents/live.txt", "-f", "message=Live shop address", "-f", "branch=live",
        "-f", ("content=" + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($address))),
        "-f", "committer[name]=Drake-Phamta", "-f", "committer[email]=$who", "-f", "author[name]=Drake-Phamta", "-f", "author[email]=$who", "--silent")
    if ($LASTEXITCODE -eq 0 -and $sha) { $body += @("-f", "sha=$sha") }
    & $gh api @body 2>$null
    return ($LASTEXITCODE -eq 0)
}
while ($true) {
    if (Test-Path $log) { Clear-Content $log }
    $p = Start-Process -FilePath $exe -ArgumentList "tunnel", "--no-autoupdate", "--url", $shop -NoNewWindow -PassThru -RedirectStandardError $log
    $url = $null
    for ($i = 0; $i -lt 60 -and -not $url -and -not $p.HasExited; $i++) {
        Start-Sleep -Seconds 1
        $m = Select-String -Path $log -Pattern "https://[a-z0-9-]+\.trycloudflare\.com" -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($m) { $url = $m.Matches[0].Value }
    }
    if ($url) {
        try { Set-Clipboard -Value $url } catch { }
        Write-Host ""
        Write-Host ("  " + (Get-Date -Format "HH:mm") + "  ABC Online Shop is public at:  $url") -ForegroundColor Green
        Write-Host "  (copied to the clipboard; the address works while this window stays open)"
        Write-Host "  Accounts: an.nguyen@example.com, sales@example.com, warehouse@example.com; password demo1234"
        if ($gh) {
            & $gh repo edit $repo --homepage $url 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) { Write-Host "  The published showcase now opens this address (GitHub repository website field)." }
            else { Write-Host "  Could not update the GitHub repository (gh auth status)." }
            if (-not (Publish-Live $url)) { Write-Host "  Could not write live.txt (branch live); the website field still works." }
        }
        Write-Host ""
        if ($first) { Start-Process $url; $first = $false }
    } else {
        Write-Host "No public address after 60 s; the log is $log"
    }
    # while the tunnel runs, watch the shop too: if it has not answered for 3 minutes (its window was closed and not
    # reopened, or the server stopped), start it again with the data kept. 3 minutes leave time for a manual restart.
    $down = 0
    while (-not $p.HasExited) {
        Start-Sleep -Seconds 30
        if (Answers) { $down = 0; continue }
        $down++
        if ($down -eq 6) {
            Write-Host ((Get-Date -Format "HH:mm") + "  the shop has not answered for 3 minutes: starting CHAY_DEMO.bat keep")
            Start-Process -FilePath (Join-Path $root "CHAY_DEMO.bat") -ArgumentList "keep" -WorkingDirectory $root
        }
        if ($down -ge 12) { $down = 0 }
    }
    Write-Host ((Get-Date -Format "HH:mm") + "  cloudflared stopped; starting it again in 10 s (close this window to stop for good)")
    Start-Sleep -Seconds 10
}
