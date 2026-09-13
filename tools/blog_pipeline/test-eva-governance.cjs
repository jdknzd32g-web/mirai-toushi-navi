const assert = require('node:assert/strict');
const fs = require('fs'), os=require('os'), path=require('path');
const {classify,check}=require('./eva-governance.cjs');
const yt='/Users/satoshioka/youtube-project-share';
assert.equal(classify(yt+'/obsidian/new-item.md').business_id,'mirai-toushi-navi');
assert.equal(classify(yt+'/channels/WAIZU/projects/new-item.md').business_id,'waizu');
assert.equal(classify(yt+'/tools/tool.py').business_id,'shared');
assert.equal(classify(yt+'/channels/another').business_id,'shared');
assert.equal(classify(yt+'_LOCAL').business_id,'unclassified');
const item={id:'test',business_id:'waizu',section:'video',title:'test',topic_id:'waizu-test',intent:'test',status:'idea',source_path:yt+'/channels/WAIZU/projects/new-item.md',reference_id:'waizu-editing-samurai-trade'};
assert.deepEqual(check([item]),[]);
assert.ok(check([{...item,business_id:'mirai-toushi-navi',section:'youtube'}]).some(e=>e.includes('mismatch')));
assert.ok(check([{...item,derived_from:'other'},{...item,id:'other',business_id:'mirai-toushi-navi',section:'youtube'}]).some(e=>e.includes('parent')));
assert.ok(check([item,item]).some(e=>e.includes('duplicate')));
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'eva-route-test-'));
const link=path.join(tmp,'waizu');
try {fs.symlinkSync(yt+'/channels/WAIZU',link);assert.equal(classify(link+'/new.md').business_id,'waizu');}
finally {fs.unlinkSync(link);fs.rmdirSync(tmp);}
console.log('10 governance checks passed');
