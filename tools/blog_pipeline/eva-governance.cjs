// Offline, read-only governance checks. No publishing or permission changes.
const fs = require('fs');
const path = require('path');
const ops = '/Users/satoshioka/eva-solution-ops/00_strategy_management';
const registry = JSON.parse(fs.readFileSync(path.join(ops,'business-registry.json'),'utf8'));
function physical(value) {
  if (!path.isAbsolute(value)) throw Error('Absolute path required');
  let current = path.resolve(value), tail = [];
  while (!fs.existsSync(current)) {
    const parent = path.dirname(current);
    if (parent === current) throw Error('Cannot resolve path');
    tail.unshift(path.basename(current)); current = parent;
  }
  return path.join(fs.realpathSync(current), ...tail);
}
function classify(value) {
  const target = physical(value);
  const match = registry.routes.map(r=>({...r,real:physical(r.path)}))
    .filter(r=>target === r.real || target.startsWith(r.real + path.sep))
    .sort((a,b)=>b.real.length-a.real.length)[0];
  return match ? {business_id:match.business_id,section:match.section,route:match.path} : {business_id:'unclassified',section:'unclassified'};
}
function check(items) {
  if (!Array.isArray(items)) return ['items must be an array'];
  const errors = [], ids = new Set();
  for (const item of items) {
    if (!item || typeof item !== 'object') {errors.push('Invalid item');continue;}
    if (!item.id || ids.has(item.id)) errors.push('Missing/duplicate id');
    ids.add(item.id);
    const business = registry.businesses[item.business_id];
    if (!business || !business.sections.includes(item.section)) errors.push(item.id+': invalid business/section');
    for (const key of ['title','topic_id','intent','status','source_path']) if (typeof item[key] !== 'string' || !item[key]) errors.push(item.id+': missing '+key);
    if (!['idea','research','draft','review','ready','published','blocked','archived'].includes(item.status)) errors.push(item.id+': invalid status');
    try {if (item.source_path && classify(item.source_path).business_id !== item.business_id) errors.push(item.id+': path business mismatch');}
    catch(e) {errors.push(item.id+': '+e.message);}
    if (item.derived_from && (item.derived_from === item.id || !items.some(p=>p.id === item.derived_from && p.business_id === item.business_id && p.topic_id === item.topic_id))) errors.push(item.id+': invalid cross-section parent');
    if (item.reference_id && !registry.references.some(r=>r.id === item.reference_id && r.consumer_business === item.business_id)) errors.push(item.id+': invalid editing reference');
  }
  return errors;
}
if (require.main === module) {
  try {
    if (process.argv[2] === 'classify') console.log(JSON.stringify(classify(process.argv[3]),null,2));
    else if (process.argv[2] === 'check') {
      const {items} = JSON.parse(fs.readFileSync(process.argv[3] || path.join(ops,'business-work-items.json'),'utf8'));
      const errors = check(items);
      console.log(JSON.stringify({status:errors.length?'blocked':'pass',items:items?.length,errors},null,2));
      process.exitCode = errors.length ? 1 : 0;
    } else throw Error('Use classify <absolute path> or check [work-items.json]');
  } catch(e) {console.error(e.message);process.exitCode=1;}
}
module.exports = {classify,check,registry};
