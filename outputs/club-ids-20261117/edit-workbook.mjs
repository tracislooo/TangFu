import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';

const directory = path.dirname(fileURLToPath(import.meta.url));
const source = 'K:/桌面/27skin/PICTURE/country-new/ALL_clubs_coordinates_latest.xlsx';
const verify = process.argv.includes('--verify');
const input = verify ? path.join(directory, 'ALL_clubs_coordinates_latest_球队ID.xlsx') : source;
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(input));
console.log((await workbook.inspect({kind:'sheet', include:'id,name', maxChars:2000})).ndjson);
if (verify) {
  const sheet = workbook.worksheets.getItemAt(0);
  const matches = JSON.parse(await fs.readFile(path.join(directory, 'matches.json'), 'utf8'));
  const actual = sheet.getRange('R2:R857').values;
  for (const row of matches) {
    if (String(actual[row.row - 2][0] ?? '') !== String(row.uid ?? '')) throw new Error(`ID mismatch at row ${row.row}`);
  }
  const preview = await workbook.render({sheetName:sheet.name, range:'N1:R10', scale:1.2, format:'png'});
  await fs.writeFile(path.join(directory, 'final-preview.png'), new Uint8Array(await preview.arrayBuffer()));
  console.log(JSON.stringify({verified:matches.filter(row=>row.club).length, selectedEgyptId:sheet.getRange('R752').values[0][0]}));
} else if (process.argv.includes('--inspect')) {
  for (let i = 0; i < 2; i++) {
    const sheet = workbook.worksheets.getItemAt(i);
    const preview = await workbook.render({sheetName:sheet.name, range:i===0?'E1:J8':'A1:D6', scale:1.2, format:'png'});
    await fs.writeFile(path.join(directory, `before-${i}.png`), new Uint8Array(await preview.arrayBuffer()));
  }
} else {
  const matches = JSON.parse(await fs.readFile(path.join(directory, 'matches.json'), 'utf8'));
  const sheet = workbook.worksheets.getItemAt(0);
  sheet.getRange('R1').copyFrom(sheet.getRange('E1'), 'all');
  sheet.getRange('R1').values = [['球队ID']];
  sheet.getRange(`R2:R${matches.length + 1}`).copyFrom(sheet.getRange(`E2:E${matches.length + 1}`), 'all');
  sheet.getRange(`R2:R${matches.length + 1}`).values = matches.map(row => [row.uid === null ? null : String(row.uid)]);
  sheet.getRange(`R1:R${matches.length + 1}`).setNumberFormat('@');
  sheet.getRange(`R1:R${matches.length + 1}`).format.columnWidth = 16;
  await workbook.recalculate();
  const preview = await workbook.render({sheetName:sheet.name, range:'N1:R10', scale:1.3, format:'png'});
  await fs.writeFile(path.join(directory, 'after.png'), new Uint8Array(await preview.arrayBuffer()));
  const output = await SpreadsheetFile.exportXlsx(workbook);
  await output.save(path.join(directory, 'ALL_clubs_coordinates_latest_球队ID.xlsx'));
  console.log(JSON.stringify({output:path.join(directory, 'ALL_clubs_coordinates_latest_球队ID.xlsx'), matched:matches.filter(row=>row.uid!==null).length, pending:matches.filter(row=>row.uid===null).length}));
}
