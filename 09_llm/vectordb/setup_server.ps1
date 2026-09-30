# Qdrant 서버(네이티브 Windows 바이너리) 설치 스크립트.
# Docker / WSL / 관리자 권한 없이 localhost:6333 서버를 띄울 수 있게 준비한다.
#
#   .\setup_server.ps1
#
# 내려받는 것:
#   - qdrant.exe                         (공식 릴리스, ~85MB)
#   - static/  (Qdrant Web UI dist)      대시보드용 정적 파일. 없으면 /dashboard 가 404.

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$QdrantVersion = "v1.19.1"   # qdrant-client 버전과 맞출 것
$WebUiVersion = "v0.2.18"

$ServerDir = Join-Path $PSScriptRoot "server"
New-Item -ItemType Directory -Force $ServerDir | Out-Null

# 1) 서버 바이너리
$exe = Join-Path $ServerDir "qdrant.exe"
if (Test-Path $exe) {
    Write-Host "qdrant.exe 이미 있음 -> 건너뜀 ($(& $exe --version))"
} else {
    $zip = Join-Path $ServerDir "qdrant.zip"
    $url = "https://github.com/qdrant/qdrant/releases/download/$QdrantVersion/qdrant-x86_64-pc-windows-msvc.zip"
    Write-Host "qdrant $QdrantVersion 내려받는 중..."
    Invoke-WebRequest -Uri $url -OutFile $zip
    Expand-Archive -Path $zip -DestinationPath $ServerDir -Force
    Remove-Item $zip
    Write-Host "설치 완료: $(& $exe --version)"
}

# 2) 대시보드 정적 파일
$static = Join-Path $ServerDir "static"
if (Test-Path (Join-Path $static "index.html")) {
    Write-Host "static/ 이미 있음 -> 건너뜀"
} else {
    $zip = Join-Path $ServerDir "webui.zip"
    $url = "https://github.com/qdrant/qdrant-web-ui/releases/download/$WebUiVersion/dist-qdrant.zip"
    Write-Host "Web UI $WebUiVersion 내려받는 중..."
    Invoke-WebRequest -Uri $url -OutFile $zip
    $tmp = Join-Path $env:TEMP "qdrant_webui_$(Get-Random)"
    Expand-Archive -Path $zip -DestinationPath $tmp -Force
    Remove-Item $zip
    Remove-Item -Recurse -Force $static -ErrorAction SilentlyContinue
    # 압축 안에 dist/ 로 들어 있으므로 static/ 으로 옮긴다.
    Move-Item (Join-Path $tmp "dist") $static
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
    Write-Host "Web UI 설치 완료"
}

Write-Host ""
Write-Host "준비 완료. 서버 실행: .\start_server.ps1"
