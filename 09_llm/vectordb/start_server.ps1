# Qdrant 서버를 localhost:6333 에서 실행한다.
#
#   .\start_server.ps1
#
# 종료는 Ctrl+C. 데이터는 server\storage\ 에 저장되어 재시작해도 유지된다.
# qdrant.exe 는 정적 파일(static/)과 저장소(storage/)를 현재 디렉터리 기준으로 찾으므로
# 반드시 server 디렉터리에서 실행해야 한다.

$ErrorActionPreference = "Stop"

$ServerDir = Join-Path $PSScriptRoot "server"
$exe = Join-Path $ServerDir "qdrant.exe"

if (-not (Test-Path $exe)) {
    Write-Error "qdrant.exe 가 없습니다. 먼저 .\setup_server.ps1 을 실행하세요."
}

if (Get-NetTCPConnection -LocalPort 6333 -ErrorAction SilentlyContinue) {
    Write-Error "6333 포트가 이미 사용 중입니다. 기존 서버가 떠 있는지 확인하세요."
}

Write-Host "REST      : http://localhost:6333"
Write-Host "대시보드  : http://localhost:6333/dashboard"
Write-Host "헬스체크  : http://localhost:6333/healthz"
Write-Host "종료      : Ctrl+C"
Write-Host ""

Push-Location $ServerDir
try {
    & $exe
} finally {
    Pop-Location
}
