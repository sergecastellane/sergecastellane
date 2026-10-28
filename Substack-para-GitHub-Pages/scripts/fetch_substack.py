import json, urllib.request, xml.etree.ElementTree as ET
from html.parser import HTMLParser
from datetime import datetime, timezone
from pathlib import Path
class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style'): self.skip+=1
        if tag in ('p','div','br','h1','h2','h3','li','blockquote'): self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
        if tag in ('p','div','li'): self.parts.append('\n')
    def handle_data(self,data):
        if not self.skip: self.parts.append(data)
req=urllib.request.Request('https://thefortyresidence.substack.com/feed',headers={'User-Agent':'AcademicWebsiteRSSReader/1.0'})
with urllib.request.urlopen(req,timeout=45) as response:
    root=ET.fromstring(response.read())
posts=[]
for item in root.findall('./channel/item')[:30]:
    html=item.findtext('{http://purl.org/rss/1.0/modules/content/}encoded') or item.findtext('description') or ''
    parser=Text(); parser.feed(html)
    posts.append({'title':item.findtext('title') or '', 'link':item.findtext('link') or '', 'text': ''.join(parser.parts).strip()})
if root.find('channel') is None: raise RuntimeError('La respuesta no es un RSS válido')
Path('substack-posts.json').write_text(json.dumps({'updated':datetime.now(timezone.utc).isoformat(),'posts':posts},ensure_ascii=False),encoding='utf-8')
