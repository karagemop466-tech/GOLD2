const assert=require('node:assert/strict');const {goldContent}=require('../site/app.js');
assert.deepEqual(goldContent(null,14,null),{fine:null,value:null});
assert.deepEqual(goldContent(6,18,100),{fine:4.5,value:450});
assert.deepEqual(goldContent(6,14,null),{fine:3.5,value:null});
for(const w of [0,-1,NaN,Infinity,'6'])assert.equal(goldContent(w,14,100).fine,null);
for(const k of [0,-1,25,Infinity,null])assert.equal(goldContent(6,k,100).fine,null);
console.log('PASS calculator: null, invalid, nominal mass and value cases (synthetic test inputs only).');
