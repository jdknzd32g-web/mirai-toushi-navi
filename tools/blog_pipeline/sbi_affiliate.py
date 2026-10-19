import html,re

URL='https://h.accesstrade.net/sp/cc?rk=0100poxk00nng7'
LABEL='SBI証券の公式サイトを確認する'
STYLESHEET='/assets/editorial/sbi-affiliate.css'
NOTICE='<p class="sbi-pr-notice" data-sbi-pr="true"><strong>PR</strong> 本記事には広告・プロモーションが含まれます。</p>'
CTA='<aside class="sbi-affiliate-cta" data-sbi-affiliate="true" aria-label="SBI証券の公式情報"><h3>SBI証券の最新情報を確認する</h3><p>サービスの条件・手数料は、公式サイトでご確認ください。</p><a class="affiliate-button" href="'+URL+'" target="_blank" rel="nofollow sponsored noopener noreferrer">'+LABEL+'</a></aside>'

def applies(article):
 return bool(re.search(r'SBI|ＳＢＩ',' '.join(str(article.get(k,'')) for k in ['path','title','category']),re.I))

def stylesheet(page):
 link='<link rel="stylesheet" href="'+STYLESHEET+'">'
 if link not in page:page=page.replace('</head>',link+'\n</head>',1)
 return page
