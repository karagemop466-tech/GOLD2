'use strict';
function goldContent(weight,karat,spot){
  if(!Number.isFinite(weight)||weight<=0||!Number.isFinite(karat)||karat<=0||karat>24)return {fine:null,value:null};
  const fine=weight*karat/24;
  return {fine,value:Number.isFinite(spot)&&spot>0?fine*spot:null};
}
if(typeof module!=='undefined')module.exports={goldContent};
if(typeof document!=='undefined'){
 const search=document.querySelector('#search');
 if(search)search.addEventListener('input',()=>{let count=0;document.querySelector('table').querySelectorAll('tbody tr').forEach(row=>{row.hidden=!row.textContent.toLowerCase().includes(search.value.toLowerCase());if(!row.hidden)count++;});document.querySelector('#filter-status').textContent=count+' matching settings';});
 const select=document.querySelector('#ring-select');
 if(select)fetch('data.json').then(r=>{if(!r.ok)throw Error('Research data unavailable');return r.json();}).then(data=>{
  function update(){const p=data[Number(select.value)];const result=goldContent(p.weightGrams,p.karat,p.spotUSDPerGram);for(const [id,value] of Object.entries({weight:p.weightGrams,fine:result.fine,spot:p.spotUSDPerGram,value:result.value}))document.getElementById(id).textContent=value===null?'':Number(value).toFixed(4);document.querySelector('#calc-title').textContent=result.fine===null?'Calculation unavailable':'Nominal gold content';}select.addEventListener('change',update);update();
 }).catch(()=>{document.querySelector('#calc-message').textContent='Research data could not be loaded. No calculation performed.';});
 const cw=document.querySelector('#custom-weight'),ck=document.querySelector('#custom-karat'),cs=document.querySelector('#custom-spot');
 if(cw&&ck){
  const runCustom=()=>{const wv=cw.value.trim()===''?null:Number(cw.value);const kv=Number(ck.value);const sv=cs&&cs.value.trim()!==''?Number(cs.value):null;const r=goldContent(wv,kv,sv);document.getElementById('custom-fine').textContent=r.fine===null?'—':r.fine.toFixed(3)+' g';document.getElementById('custom-value').textContent=r.value===null?'—':'$'+r.value.toFixed(2);};
  [cw,ck,cs].filter(Boolean).forEach(el=>{el.addEventListener('input',runCustom);el.addEventListener('change',runCustom);});
  runCustom();
 }
}
