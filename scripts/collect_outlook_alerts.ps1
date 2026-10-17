$ErrorActionPreference = 'Stop'
$destination = Join-Path (Split-Path $PSScriptRoot -Parent) 'local-data\property-alerts'
New-Item -ItemType Directory -Force -Path $destination | Out-Null
try {
    $outlook = New-Object -ComObject Outlook.Application
    $namespace = $outlook.GetNamespace('MAPI')
    $inbox = $namespace.GetDefaultFolder(6)
    $items = $inbox.Items
    $items.Sort('[ReceivedTime]', $true)
    $limit = [Math]::Min($items.Count, 800)
    $saved = 0
    for ($i = 1; $i -le $limit; $i++) {
        $mail = $items.Item($i)
        if (-not $mail -or $mail.MessageClass -notlike 'IPM.Note*') { continue }
        $sender = [string]$mail.SenderEmailAddress
        try { $sender = [string]$mail.PropertyAccessor.GetProperty('http://schemas.microsoft.com/mapi/proptag/0x39FE001E') } catch {}
        $senderLower = $sender.ToLowerInvariant()
        if ($senderLower -notmatch '@(?:[^.]+\.)?(?:ddproperty\.com|propertyhub\.in\.th)$') { continue }
        $received = [datetime]$mail.ReceivedTime
        if ($received -lt (Get-Date).AddDays(-45)) { break }
        $html = [string]$mail.HTMLBody
        if (-not $html) { continue }
        $bodyText = [regex]::Replace($html, '(?is)<(script|style)\b[^>]*>.*?</\1>', ' ')
        $bodyText = [regex]::Replace($bodyText, '(?is)<br\s*/?>|</(?:p|div|li|tr|td|h[1-6])\s*>', ' ')
        $bodyText = [regex]::Replace($bodyText, '(?is)<[^>]+>', ' ')
        $bodyText = [System.Net.WebUtility]::HtmlDecode($bodyText) -replace '\s+', ' '
        $links = New-Object System.Collections.Generic.List[string]
        $anchorMatches = [regex]::Matches($html, '(?is)<a\b[^>]*href\s*=\s*["'']([^"'']+)["''][^>]*>(.*?)</a>')
        foreach ($anchor in $anchorMatches) {
            $url = [System.Net.WebUtility]::HtmlDecode($anchor.Groups[1].Value)
            if ($url -notmatch '^https?://(?:www\.)?(?:propertyhub\.in\.th/(?:en/)?listings/|ddproperty\.com/(?:en/)?(?:property|listing|condo)/)') { continue }
            $label = [regex]::Replace($anchor.Groups[2].Value, '(?is)<[^>]+>', ' ')
            $label = [System.Net.WebUtility]::HtmlDecode(($label -replace '\s+', ' ')).Trim()
            if (-not $label) { continue }
            $snippet = ''
            $position = $bodyText.IndexOf($label, [StringComparison]::OrdinalIgnoreCase)
            if ($position -ge 0) {
                $start = [Math]::Max(0, $position - 180)
                $length = [Math]::Min($bodyText.Length - $start, $label.Length + 360)
                $snippet = $bodyText.Substring($start, $length)
            }
            $snippet = [regex]::Replace($snippet, '\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b|(?:\+?\d[\d ()-]{7,}\d)', ' ')
            $snippet = [regex]::Replace($snippet, '\s+', ' ').Trim()
            $safeUrl = [System.Net.WebUtility]::HtmlEncode($url)
            $safeLabel = [System.Net.WebUtility]::HtmlEncode($label)
            $safeSnippet = [System.Net.WebUtility]::HtmlEncode($snippet)
            $links.Add("<p><a href=`"$safeUrl`">$safeLabel</a> <span>$safeSnippet</span></p>")
        }
        if ($links.Count -eq 0) { continue }
        $hashBytes = [System.Security.Cryptography.SHA256]::Create().ComputeHash([Text.Encoding]::UTF8.GetBytes([string]$mail.EntryID))
        $fileName = ([BitConverter]::ToString($hashBytes).Replace('-', '').Substring(0, 24).ToLowerInvariant()) + '.html'
        $htmlPath = Join-Path $destination $fileName
        if (-not (Test-Path -LiteralPath $htmlPath)) {
            # Keep only source listing links and their labels. Do not persist full email bodies or contacts.
            $safeSubject = [string]$mail.Subject
            $safeSubject = [regex]::Replace($safeSubject, '\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b|(?:\+?\d[\d ()-]{7,}\d)', '')
            $safeSubject = [System.Net.WebUtility]::HtmlEncode($safeSubject)
            [IO.File]::WriteAllText($htmlPath, "<html><body><h1>$safeSubject</h1>$($links -join [Environment]::NewLine)</body></html>", [Text.Encoding]::UTF8)
            $saved++
        }
    }
    Write-Output "Saved $saved new portal alert emails."
} catch {
    Write-Output 'Outlook classic is not available or has no signed-in profile. Add .eml/.html alert emails to local-data\property-alerts to import them.'
}
