import {loadResearch, validateResearch, saveReport} from './lib.mjs';
const research = await loadResearch();
const result = validateResearch(research);
await saveReport('evidence-audit.json', {checkedAt:new Date().toISOString(), ...result, limitation:'Structural/provenance consistency checks only; not independent factual verification or physical authentication.'});
if (result.errors.length) {
  console.error(result.errors.join('\n')); process.exitCode = 1;
} else {
  console.log(`PASS evidence consistency: ${result.counts.products} products, ${result.counts.sources} source records, ${result.counts.findings} findings; ${result.counts.purchaseReady} purchase approvals.`);
  console.log(`${result.warnings.length} non-blocking review warnings recorded in test-results/evidence-audit.json. Unknowns stay blank; automated tests cannot certify truth.`);
}
