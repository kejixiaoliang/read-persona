param(
  [string]$Output = "",
  [string]$SkillVersion = "1.0.3",
  [int]$RecommendCount = 12,
  [int]$NotebookPageSize = 100,
  [int]$MaxNotebookPages = 3,
  [int]$TimeoutSec = 20,
  [switch]$SkipRecommendations
)

$ErrorActionPreference = "Stop"
$GatewayUrl = "https://i.weread.qq.com/api/agent/gateway"

function Get-WeReadApiKey {
  $key = [Environment]::GetEnvironmentVariable("WEREAD_API_KEY", "Process")
  if ([string]::IsNullOrWhiteSpace($key)) {
    $key = [Environment]::GetEnvironmentVariable("WEREAD_API_KEY", "User")
  }
  if ([string]::IsNullOrWhiteSpace($key)) {
    throw "WEREAD_API_KEY is missing. Get a key at https://weread.qq.com/r/weread-skills and set it as an environment variable."
  }
  return $key
}

function Invoke-WeReadApi {
  param(
    [hashtable]$Payload,
    [string]$ApiKey
  )

  $Payload["skill_version"] = $SkillVersion
  $json = $Payload | ConvertTo-Json -Compress -Depth 20
  $response = Invoke-WebRequest `
    -Method Post `
    -Uri $GatewayUrl `
    -Headers @{ Authorization = "Bearer $ApiKey"; "Content-Type" = "application/json" } `
    -Body $json `
    -TimeoutSec $TimeoutSec `
    -UseBasicParsing

  if ([string]::IsNullOrWhiteSpace($response.Content)) {
    throw "WeRead API returned an empty response."
  }
  $data = $response.Content | ConvertFrom-Json
  if ($null -ne $data.errcode -and [int]$data.errcode -ne 0) {
    $message = if ($data.errmsg) { $data.errmsg } elseif ($data.errlog) { $data.errlog } else { ($data | ConvertTo-Json -Compress) }
    throw "WeRead API error $($data.errcode): $message"
  }
  return $data
}

function Get-Notebooks {
  param([string]$ApiKey)

  $allBooks = @()
  $lastSort = $null
  $hasMore = 1
  $pages = 0
  $totalBookCount = $null
  $totalNoteCount = $null

  while ($hasMore -eq 1 -and $pages -lt $MaxNotebookPages) {
    $payload = @{ api_name = "/user/notebooks"; count = $NotebookPageSize }
    if ($null -ne $lastSort) {
      $payload["lastSort"] = $lastSort
    }
    $page = Invoke-WeReadApi -Payload $payload -ApiKey $ApiKey
    $pages += 1
    if ($null -ne $page.totalBookCount) { $totalBookCount = $page.totalBookCount }
    if ($null -ne $page.totalNoteCount) { $totalNoteCount = $page.totalNoteCount }
    $books = @($page.books)
    $allBooks += $books
    $hasMore = if ($null -ne $page.hasMore) { [int]$page.hasMore } else { 0 }
    if ($books.Count -eq 0) { break }
    $lastSort = $books[-1].sort
    if ($null -eq $lastSort) { break }
  }

  return [ordered]@{
    totalBookCount = $totalBookCount
    totalNoteCount = $totalNoteCount
    books = $allBooks
    fetchedPages = $pages
    truncated = [bool]($hasMore -eq 1 -and $pages -ge $MaxNotebookPages)
  }
}

$apiKey = Get-WeReadApiKey
$modes = @("overall", "annually", "monthly", "weekly")
$reading = [ordered]@{}
foreach ($mode in $modes) {
  $reading[$mode] = Invoke-WeReadApi -Payload @{ api_name = "/readdata/detail"; mode = $mode } -ApiKey $apiKey
}

$recommendations = if ($SkipRecommendations) {
  [ordered]@{ books = @(); skipped = $true }
} else {
  Invoke-WeReadApi -Payload @{ api_name = "/book/recommend"; count = $RecommendCount; maxIdx = 0 } -ApiKey $apiKey
}

$payload = [ordered]@{
  generatedAt = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
  source = [ordered]@{
    gateway = $GatewayUrl
    skillVersion = $SkillVersion
    modes = $modes
  }
  shelf = Invoke-WeReadApi -Payload @{ api_name = "/shelf/sync" } -ApiKey $apiKey
  reading = $reading
  notebooks = Get-Notebooks -ApiKey $apiKey
  recommendations = $recommendations
}

$text = $payload | ConvertTo-Json -Depth 40
if ([string]::IsNullOrWhiteSpace($Output)) {
  $text
} else {
  $parent = Split-Path -Parent $Output
  if (-not [string]::IsNullOrWhiteSpace($parent) -and -not (Test-Path -LiteralPath $parent)) {
    New-Item -ItemType Directory -Path $parent | Out-Null
  }
  Set-Content -LiteralPath $Output -Value $text -Encoding UTF8
}
