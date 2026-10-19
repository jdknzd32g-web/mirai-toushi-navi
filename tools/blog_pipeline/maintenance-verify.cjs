const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {createRequire}=require('module');
const {chromium}=createRequire('/Users/satoshioka/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/package.json')('playwright');
const URL='https://h.accesstrade.net/sp/cc?rk=0100poxk00nng7',LABEL='SBI証券の公式サイトを確認する';
async function inspect(page,article){return page.evaluate(({article,URL,LABEL})=>{
 const errors=[],$=s=>document.querySelector(s),all=s=>[...document.querySelectorAll(s)],norm=s=>s.replace(/\s+/g,' ').trim();
 if(all('h1').length!==1||norm($('h1')?.textContent||'')!==norm(article.title))errors.push('h1');
 if(document.documentElement.scrollWidth>innerWidth+1)errors.push('overflow');
 if(all('img').some(i=>!i.complete||!i.naturalWidth))errors.push('images');
 if(article.is_sbi){
  const summary=$('.bp-summary,.summary-box'),footer=summary?.nextElementSibling,notice=all('[data-sbi-pr]');
  if(!footer?.matches('.sbi-affiliate-cta'))errors.push('summary-footer-position');
  if(all('.sbi-affiliate-cta').length!==1)errors.push('footer-count');
  const button=footer?.querySelector('a');
  if(!button||button.href!==URL||norm(button.textContent)!==LABEL)errors.push('affiliate-url-or-label');
  if(button&&(!['nofollow','sponsored','noopener'].every(x=>button.relList.contains(x))||button.target!=='_blank'))errors.push('affiliate-rel');
  if(button){const r=button.getBoundingClientRect(),css=getComputedStyle(button);if(r.height<44||parseFloat(css.fontSize)<16||r.right>innerWidth+1||r.left<0)errors.push('affiliate-mobile-size');}
  if(notice.length!==1||!(/\bPR\b/.test(notice[0]?.textContent||'')))errors.push('pr-disclosure');
  if(notice[0]){const css=getComputedStyle(notice[0]);if(css.display==='none'||css.visibility==='hidden'||Number(css.opacity)===0||parseFloat(css.fontSize)<16)errors.push('pr-visibility');const lead=$('.bp-lead,.lead');if(lead&&!(notice[0].compareDocumentPosition(lead)&Node.DOCUMENT_POSITION_FOLLOWING))errors.push('pr-intro-position');}
  const canonical=$('link[rel="canonical"]');const expectedCanonical=article.path==='blog/sbi-securities/index.html'?'https://eva-solution.com/blog/sbi-securities/':'https://eva-solution.com/'+article.path;if(canonical&&canonical.href!==expectedCanonical)errors.push('canonical');
  if(article.path.endsWith('/zero-commission-status.html')){const text=document.body.innerText;if(!text.includes('原則として郵送へ戻せない'))errors.push('electronic-delivery-notice');const schemas=all('script[type="application/ld+json"]').map(s=>{try{return JSON.parse(s.textContent)}catch{return{}}});const a=schemas.find(s=>s['@type']==='Article');if(!a||a.datePublished!=='2026-10-18'||a.dateModified!=='2026-10-19')errors.push('schema-dates');}
 }
 if(article.path==='blog/2025/region2/region2.html'&&all('link[rel="stylesheet"]').some(n=>n.href.endsWith('/blog/css/blog-style.css')))errors.push('obsolete-css');
 return errors;
},{article,URL,LABEL});}
async function main({root,out,base,deploy,manifest,siteDir,local=false,production=false}){
 if(!local&&!process.argv.includes('--no-x'))throw Error('Maintenance verification requires --no-x');
 if(manifest.verification_profile!=='sbi_maintenance'||manifest.no_sns!==true)throw Error('Wrong maintenance manifest');
 fs.mkdirSync(out,{recursive:true});siteDir=siteDir||path.join(out,'site');
 for(const name of manifest.files){const h=crypto.createHash('sha1').update(fs.readFileSync(path.join(siteDir,name))).digest('hex');if(h!==manifest.hashes[name])throw Error('Package changed:'+name);}
 const report={status:'blocked',deploy:deploy.id,base,checked_at:new Date().toISOString(),widths:[1440,768,390,320],checks:[],negative_tests:[],errors:[],no_sns:true,verification_profile:manifest.verification_profile,package_hashes:manifest.hashes,checker_sha256:crypto.createHash('sha256').update(fs.readFileSync(__filename)).digest('hex')};
 const catalog=JSON.parse(fs.readFileSync(path.join(out,'article-catalog.json')));const targets=catalog.filter(a=>manifest.articles.includes(a.path)||manifest.support_pages.includes(a.path));
 if(targets.filter(a=>a.is_sbi).length!==45)throw Error('Expected all45 SBI articles');
 const browser=await chromium.launch({channel:'chrome',headless:true});
 try{for(const width of report.widths){
  const context=await browser.newContext({viewport:{width,height:960},reducedMotion:'reduce'});
  const baseURL=new global.URL(base);await context.route('**/*',route=>{const u=new global.URL(route.request().url());if(u.origin===baseURL.origin)return route.continue();if(['eva-solution.com','eva-solution.netlify.app'].includes(u.hostname))return route.continue({url:baseURL.origin+u.pathname+u.search});return route.abort();});
  const page=await context.newPage();
  async function load(a){const r=await page.goto(base+'/'+a.path,{waitUntil:'load'});await page.evaluate(async()=>{for(const i of document.images)i.loading='eager';await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));await document.fonts.ready;});return r;}
  for(const a of targets){const response=await load(a);const errors=await inspect(page,a);if(!response.ok())errors.push('HTTP:'+response.status());report.checks.push({width,page:a.path,status:errors.length?'blocked':'pass',errors});report.errors.push(...errors.map(e=>width+':'+a.path+':'+e));
   if(a.is_sbi&&(width===390||width===320)&&!errors.length){const name=path.basename(a.path,'.html');await page.locator('.sbi-affiliate-cta').screenshot({path:path.join(out,`affiliate-${name}-${width}.png`)});await page.locator('[data-sbi-pr]').screenshot({path:path.join(out,`pr-${name}-${width}.png`)});}
  }
  if(width===390){const a=targets.find(a=>a.path.endsWith('/zero-commission-status.html'));for(const name of ['missing-pr','wrong-url','missing-rel','duplicate-footer','wrong-position','wrong-label','small-font','overflow']){await load(a);await page.evaluate(name=>{const f=document.querySelector('.sbi-affiliate-cta'),a=f.querySelector('a');if(name==='missing-pr')document.querySelector('[data-sbi-pr]').remove();if(name==='wrong-url')a.href='https://example.invalid/';if(name==='missing-rel')a.rel='';if(name==='duplicate-footer')f.after(f.cloneNode(true));if(name==='wrong-position')document.querySelector('.bp-summary').before(f);if(name==='wrong-label')a.textContent='申込';if(name==='small-font')a.style.setProperty('font-size','9px','important');if(name==='overflow'){a.style.width='1000px';a.style.maxWidth='none';}},name);const errors=await inspect(page,a);report.negative_tests.push({name,detected:errors.length>0,errors});if(!errors.length)report.errors.push('Negative test missed:'+name);}}
  await context.close();
 }
 report.status=report.errors.length?'blocked':'pass';
 }catch(e){report.errors.push(e.stack);}finally{await browser.close();}
 if(report.errors.length)report.status='blocked';fs.writeFileSync(path.join(out,local?'local-verified.json':production?'production-verified.json':'verified.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({status:report.status,deploy:report.deploy,base,checks:report.checks.length,negative_tests:report.negative_tests.length,errors:report.errors}));if(report.status!=='pass')process.exitCode=1;return report;
}
exports.main=main;
if(require.main===module){const out=process.env.MAINTENANCE_OUT;const manifest=JSON.parse(fs.readFileSync(process.env.MAINTENANCE_MANIFEST));main({root:'/Users/satoshioka/mirai-toushi-navi',out,base:process.env.MAINTENANCE_BASE,deploy:{id:'local-maintenance'},manifest,siteDir:process.env.MAINTENANCE_SITE,local:true}).catch(e=>{console.error(e.message);process.exitCode=1});}
