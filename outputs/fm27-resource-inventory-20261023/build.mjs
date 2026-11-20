import fs from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const dir=fileURLToPath(new URL('.',import.meta.url));
const d=JSON.parse(await fs.readFile(`${dir}/inventory.json`,'utf8'));
const w=Workbook.create();
const hdr=['资源名称 / 文件名','Path ID','inlineStyle Path ID','CAB 名称','Bundle 名称','资源类型','记录状态','资源键 / GUID','inlineStyle 所在 CAB'];
const specs=[
 ['界面与逻辑',hdr,d.ui,[60,25,25,45,76,22,24,48,45],'以当前游戏安装资源为准；前四项依次为第一至第四版概览。'],
 ['内联样式',hdr,d.styles,[60,25,25,45,76,22,24,48,45],'样式对象单独记录；其自身没有 inlineSheet，所属界面的样式编号见“界面与逻辑”。'],
 ['图片与字体',[...hdr,'宽度 px','高度 px'],d.graphics,[42,25,25,45,76,20,45,48,45,14,14],'446 张图片及 9 个字体相关对象；已有自定义图片与新增图片分开标注。'],
 ['Bundle与配置',['Bundle / 配置文件名','CAB 名称','游戏安装路径','皮肤包路径','当前 SHA-256','资源记录数','游戏与皮肤包核对'],d.bundles,[78,45,100,78,70,16,38],'Bundle 是物理文件；CAB 是包内序列化文件；Path ID 必须与 CAB / Bundle 一起定位。']
];
let ix=0;
for(const [name,heads,rows,widths,note] of specs){
 const s=w.worksheets.add(name);s.showGridLines=false;s.tabColor=ix===0?'#146F83':'#455B73';
 const last=String.fromCharCode(64+heads.length);const n=rows.length+5;
 const full=s.getRange(`A1:${last}${n}`);full.format.font={name:'Microsoft YaHei',size:10,color:'#233448'};full.format.rowHeight=23;full.format.verticalAlignment='center';
 s.getRange('A1').values=[[`FM27 当前修改资源清单 · ${name}`]];s.getRange(`A1:${last}1`).merge();s.getRange('A1').format.font={name:'Microsoft YaHei',size:15,bold:true,color:'#146F83'};s.getRange('A1').format.rowHeight=32;
 const notes=[note,`提取日期：${d.date} ｜ 本表 ${rows.length} 项 ｜ 所有长编号均以文本保存，保留精度。`,name==='Bundle与配置'?'下方附目录文件与已保存布局；这些配置不属于 CAB 对象，Path ID 不适用。':'范围：相对 2026-10-22 重置基线的新增/修改对象，并含沿用图片、历史字体；保留的旧辅助组件也列入，未逐项断言当前可达。'];
 notes.forEach((x,i)=>{s.getRange(`A${i+2}:${last}${i+2}`).merge();s.getRange(`A${i+2}`).values=[[x]];s.getRange(`A${i+2}`).format.font={name:'Microsoft YaHei',size:10,color:'#667788'};});
 s.getRange(`A5:${last}5`).values=[heads];
 if(rows.length)s.getRange(`A6:${last}${n}`).values=rows;
 s.getRange(`A5:${last}5`).format={fill:'#213C53',font:{name:'Microsoft YaHei',size:10,bold:true,color:'#FFFFFF'},rowHeight:30};
 widths.forEach((v,j)=>s.getRange(`${String.fromCharCode(65+j)}1:${String.fromCharCode(65+j)}${n}`).format.columnWidth=v);
 if(name!=='Bundle与配置'){
  s.getRange(`B6:C${n}`).setNumberFormat('@');
  s.getRange(`B6:C${n}`).formulas=rows.map(r=>r.slice(1,3).map(v=>`="${v}"`));
 }
 else {s.getRange(`C6:D${n}`).format.wrapText=true;s.getRange(`A6:G${n}`).format.rowHeight=62;}
 for(let r=6;r<=n;r+=2)s.getRange(`A${r}:${last}${r}`).format.fill='#EFF5F8';
 s.tables.add(`A5:${last}${n}`,true,`Inventory${++ix}`);
 s.freezePanes.freezeRows(5);s.freezePanes.freezeColumns(1);
 if(name==='Bundle与配置'){
  const r=n+4;const ch=['配置文件名','用途','Path ID','inlineStyle Path ID','CAB 名称','文件路径','SHA-256'];
  s.getRange(`A${r}:G${r}`).values=[ch];s.getRange(`A${r}:G${r}`).format={fill:'#213C53',font:{name:'Microsoft YaHei',size:10,bold:true,color:'#FFFFFF'}};
  s.getRange(`A${r+1}:G${r+d.config.length}`).values=d.config;
 }
}
w.recalculate();
console.log((await w.inspect({kind:'region',sheetId:'界面与逻辑',range:'A5:C10',maxChars:2400,tableMaxRows:6,tableMaxCols:3})).ndjson);
console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!',options:{useRegex:true,maxResults:20},maxChars:1500})).ndjson);
for(const [name] of specs){
 const p=await w.render({sheetName:name,range:'A5:D11',scale:1.3,format:'png'});
 await fs.writeFile(`${dir}/${name}-preview.png`,new Uint8Array(await p.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(w)).save(`${dir}/FM27_修改资源_PathID_CAB_Bundle清单.xlsx`);
console.log('Exported workbook');
