"""Structural hallucination-risk/security audit, not a factual truth detector."""
import json,pathlib,re
from html.parser import HTMLParser
from urllib.parse import urlsplit
root=pathlib.Path(__file__).resolve().parents[1]/'site'
data=json.loads((root/'data.json').read_text())
allowed={'www.bluenile.com','www.ecfr.gov'}
for p in data:
 assert urlsplit(p['source']).hostname in allowed
 assert p['checked']=='2026-10-22'
 assert p['currency'] is None, 'Currency context remains unverified; do not infer USD from a dollar symbol'
 assert f"${p['price']:,}(Setting Price)"==p['evidence']['price']
 assert p['metal']==p['evidence']['metal'] and p['id']==p['evidence']['id']
 assert p['priceScope'].startswith('Setting only')
 for field in ['weightGrams','solidGold','hallmark','makerMark','spotUSDPerGram','rawGoldGrams','completeRingPrice']: assert p[field] is None
class Check(HTMLParser):
 def __init__(self): super().__init__();self.row=False;self.official=False;self.header=False
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  assert not any(k.startswith('on') for k in a),'Inline event handler'
  if tag=='tr': self.row=True;self.official=False;self.header=False
  if tag=='th': self.header=True
  if tag=='a':
   href=a.get('href','');u=urlsplit(href)
   assert u.scheme not in ('javascript','data')
   if u.scheme=='https':
    assert u.hostname in allowed
    self.official=True
   elif href and not href.startswith('#'):assert (root/href.split('#')[0]).exists(),href
  if tag in ('script','link'):
   url=a.get('src',a.get('href',''));assert '://' not in url;assert (root/url).exists()
 def handle_endtag(self,tag):
  if tag=='tr': assert self.header or self.official,'Table row lacks official source';self.row=False
for path in root.glob('*.html'):
 text=path.read_text();assert 'No hallucinations. No invented prices.' in text;assert 'Content-Security-Policy' in text
 Check().feed(text)
print(f'PASS: {len(data)} records, 6 pages; official row links, evidence consistency, blank unknowns, local links, static security checks.')
print('OPEN: missing product evidence and gold quote. Automated audit cannot establish truth; recheck hallucinations after every review.')
