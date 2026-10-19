import re,xml.etree.ElementTree as ET
from urllib.parse import urlsplit,unquote,quote

BASE='https://eva-solution.com'
NS='http://www.sitemaps.org/schemas/sitemap/0.9'
IMAGE='http://www.google.com/schemas/sitemap-image/1.1'

def build_sitemap(raw,public_paths,articles):
 paths={str(p).lstrip('/') for p in public_paths}
 def canonical(value):
  u=urlsplit(value)
  if u.hostname not in ('eva-solution.com','www.eva-solution.com','eva-solution.netlify.app'):return None
  name=unquote(u.path).lstrip('/')
  candidates=[name,name+'index.html' if name.endswith('/') else name+'/index.html',name+'.html']
  if not name:candidates=['index.html']
  name=next((p for p in candidates if p in paths),None)
  return BASE+('/' if name=='index.html' else '/'+quote(name,safe='/-._~')) if name else None
 raw=re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)','&amp;',raw)
 tree=ET.fromstring(raw);ET.register_namespace('',NS);ET.register_namespace('image',IMAGE)
 result=ET.Element('{'+NS+'}urlset');seen=set();omitted=[]
 for entry in tree.findall('{'+NS+'}url'):
  loc=entry.find('{'+NS+'}loc');target=canonical(loc.text or '') if loc is not None else None
  if not target:omitted.append(loc.text if loc is not None else 'missing loc');continue
  if target in seen:continue
  loc.text=target;seen.add(target)
  for n in entry.iter():
   if n.tag=='{'+IMAGE+'}loc' and n.text:
    u=urlsplit(n.text)
    if u.hostname in ('eva-solution.netlify.app','www.eva-solution.com'):n.text=BASE+u.path+('?' + u.query if u.query else '')
  result.append(entry)
 for article in articles:
  name=article['path'].lstrip('/')
  if name not in paths:continue
  target=BASE+'/'+quote(name,safe='/-._~')
  if target in seen:continue
  entry=ET.SubElement(result,'{'+NS+'}url');ET.SubElement(entry,'{'+NS+'}loc').text=target;seen.add(target)
  date=article.get('checked_date') or article.get('publication_date') or article.get('date')
  if date and re.fullmatch(r'\d{4}-\d{2}-\d{2}',date):ET.SubElement(entry,'{'+NS+'}lastmod').text=date
 return ET.tostring(result,encoding='utf-8',xml_declaration=True),{'urls':len(seen),'omitted_nonpublic':omitted}
