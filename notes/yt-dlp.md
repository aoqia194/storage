Generally, the following flags are a really good baseline:

`--merge-output-format mkv` - Use mkv when merging, its a great open format.
`-o "/%(webpage_url_domain)s/%(uploader_id)s/[%(upload_date>%Y-%m-%d)s] [%(id)s] %(title)s.%(ext)s"` - A good output format, but some domains require it to be changed for parity.

`--embed-metadata` + `--embed-info-json` + `--embed-chapters` - You want chapters and infojson embedded if possible!
`--write-description` + `--write-info-json` + `--write-playlist-metafiles`

## Site differences

#### Kick.com

Output format - replace `uploader_id` with `channel`.

#### mediadelivery

Sometimes need to up the concurrent fragment downloads. Cookies need to be from the browser if the referrer uses a password cookie system. Http headers require the `Referer` header set to the correct site (sometimes `https://iframe.mediadelivery.net/` but others you need to inspect element to get it) and the `User-Agent` sometimes spoofed too. `--no-part` may need to be specified as there are a LOT of fragments. Output template needs to be modified too -- can't reliably store the webpage_url_domain, so we take out the `webpage_url_domain`, `uploader_id` and `id` variables.




