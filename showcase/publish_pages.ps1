# Publishes the project to its public GitHub repository (GitHub Pages serves it) as ONE snapshot commit on top of the
# previously published one: the local git history is not published, and the author is the GitHub noreply address.
# Published: every file tracked by git, plus the essay PDF of Bai_nop. Not published: De_bai, Luu_tru, the docx, the
# project log docs/CONTROL*.md, the sources docs/DEFENSE*.md (their readable pages are published password-protected) and
# everything else that .gitignore leaves out.
# Usage, in the project folder after committing:  powershell -NoProfile -File showcase\publish_pages.ps1
# Needs the GitHub CLI logged in (gh auth status). Keep this file ASCII only (Windows PowerShell 5.1).
param([string]$Repo = "Drake-Phamta/abc-online-shop")

$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
Set-Location -LiteralPath $root
function Fail($why) { Write-Output "NOT published: $why"; exit 1 }

if (git status --porcelain) { Fail "commit the changes first (git status is not clean)" }
$pdf = "Bai_nop/tieuluan_V4_04_10_phamtuananh_018.pdf"
if (-not (Test-Path -LiteralPath $pdf)) { Fail "$pdf is missing" }
$id = gh api user --jq .id
$login = gh api user --jq .login
if (-not $id -or -not $login) { Fail "the GitHub CLI is not logged in (gh auth login)" }
$mail = "$id+$login@users.noreply.github.com"
$url = "https://github.com/$Repo.git"
$auth = @("-c", "credential.helper=", "-c", "credential.helper=!gh auth git-credential")

# tree to publish = HEAD + the essay PDF (built in a separate index, the normal index is not touched)
$env:GIT_INDEX_FILE = Join-Path $env:TEMP "abc_publish.index"
git read-tree HEAD
$blob = git hash-object -w -- $pdf
git update-index --add --cacheinfo "100644,$blob,$pdf"
# personal notes: the project log is never published; the defence notes only as password-protected readable pages
# (tools/protect_page.mjs, password in %LOCALAPPDATA%\abc_shop\page_password.txt, outside the repository)
$private = git ls-files | Where-Object { $_ -match '^(showcase/pages/)?docs/(CONTROL|DEFENSE)(\.vi)?\.md(\.html)?$' }
if ($private) { git update-index --force-remove -- @($private) }
$pwFile = Join-Path $env:LOCALAPPDATA "abc_shop\page_password.txt"
if (Test-Path $pwFile) {
    $env:ABC_PAGE_PASSWORD = (Get-Content -Raw $pwFile).Trim()
    foreach ($page in "showcase/pages/docs/DEFENSE.md.html", "showcase/pages/docs/DEFENSE.vi.md.html") {
        if (-not (Test-Path -LiteralPath $page)) { continue }
        $tmp = Join-Path $env:TEMP ("abc_protected_" + (Split-Path $page -Leaf))
        node tools/protect_page.mjs $page $tmp | Out-Null
        if ($LASTEXITCODE -ne 0) { Remove-Item Env:ABC_PAGE_PASSWORD; Fail "could not protect $page" }
        $pblob = git hash-object -w -- $tmp
        git update-index --add --cacheinfo "100644,$pblob,$page"
        Remove-Item -LiteralPath $tmp
    }
    Remove-Item Env:ABC_PAGE_PASSWORD
} else { Write-Output "No page password ($pwFile): the defence notes are left out." }
$tree = git write-tree
Remove-Item Env:GIT_INDEX_FILE
if ($LASTEXITCODE -ne 0 -or -not $tree) { Fail "could not build the tree" }

# parent = what is published now (none the first time)
$parent = $null
git @auth fetch -q $url "+refs/heads/main:refs/publish/main" 2>$null
if ($LASTEXITCODE -eq 0) { $parent = git rev-parse refs/publish/main }
if ($parent -and (git rev-parse "$parent^{tree}") -eq $tree) { Write-Output "Nothing new to publish ($Repo is up to date)."; exit 0 }

$env:GIT_AUTHOR_NAME = $login; $env:GIT_AUTHOR_EMAIL = $mail
$env:GIT_COMMITTER_NAME = $login; $env:GIT_COMMITTER_EMAIL = $mail
$message = "Snapshot of the project (local commit " + (git rev-parse --short HEAD) + ")"
if ($parent) { $commit = git commit-tree $tree -p $parent -m $message } else { $commit = git commit-tree $tree -m $message }
git @auth push -q $url "${commit}:refs/heads/main"
if ($LASTEXITCODE -ne 0) { Fail "git push was refused" }
git update-ref refs/publish/main $commit
Write-Output "Published $commit to https://github.com/$Repo (site: https://$($login.ToLower()).github.io/$($Repo.Split('/')[1])/)"
