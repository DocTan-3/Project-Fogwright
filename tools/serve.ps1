# A tiny local web server for Fogwright, so it runs on a Windows laptop with nothing installed.
# Started by "Play Fogwright.bat" in the repository's top folder. Close this window to stop it.
param([int]$Port = 8000)
$root = Split-Path -Parent $PSScriptRoot
$types = @{ '.html' = 'text/html; charset=utf-8'; '.js' = 'application/javascript'; '.json' = 'application/json'; '.css' = 'text/css';
            '.png' = 'image/png'; '.jpg' = 'image/jpeg'; '.svg' = 'image/svg+xml' }
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$Port/")
try { $listener.Start() } catch { Write-Host "Port $Port is busy. Close the other Fogwright window, or run: serve.ps1 -Port 8010"; Read-Host 'Press Enter to close'; exit 1 }
Write-Host "Fogwright is running at http://localhost:$Port/  (close this window to stop it)"
Start-Process "http://localhost:$Port/"
while ($listener.IsListening) {
  $ctx = $listener.GetContext(); $res = $ctx.Response
  try {
    $rel = [Uri]::UnescapeDataString($ctx.Request.Url.AbsolutePath).TrimStart('/')
    if ($rel -eq '' -or $rel.EndsWith('/')) { $rel += 'index.html' }
    $file = [IO.Path]::GetFullPath((Join-Path $root $rel))
    if ($file.StartsWith($root) -and (Test-Path $file -PathType Leaf)) {
      $bytes = [IO.File]::ReadAllBytes($file); $ext = [IO.Path]::GetExtension($file).ToLower()
      $res.ContentType = $(if ($types[$ext]) { $types[$ext] } else { 'application/octet-stream' })
      $res.Headers.Add('Cache-Control', 'no-store')
      $res.ContentLength64 = $bytes.Length; $res.OutputStream.Write($bytes, 0, $bytes.Length)
    } else { $res.StatusCode = 404 }
  } catch { $res.StatusCode = 500 } finally { $res.Close() }
}
