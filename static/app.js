'use strict';
let analysis = null;
let uploadedCSV = null;
const $ = (selector) => document.querySelector(selector);
const number = (value) => new Intl.NumberFormat('ru-RU', {maximumFractionDigits: 1}).format(value);
const money = (value) => `${number(Math.round(value))} ₸`;
const dateLabel = (value) => {
  const [year,month,day]=value.split('-').map(Number);
  const months=['қаңтар','ақпан','наурыз','сәуір','мамыр','маусым','шілде','тамыз','қыркүйек','қазан','қараша','желтоқсан'];
  return `${day} ${months[month-1]} ${year}`;
};
const escapeHTML = (value) => String(value).replace(/[&<>"']/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));

function showView(name) {
  document.querySelectorAll('.view').forEach((view) => { view.hidden = view.id !== `view-${name}`; });
  document.querySelectorAll('.nav-item').forEach((button) => {
    const active = button.dataset.view === name;
    button.classList.toggle('active', active);
    if (active) button.setAttribute('aria-current', 'page'); else button.removeAttribute('aria-current');
  });
  $('#breadcrumb').textContent = document.querySelector(`[data-view="${name}"]`).textContent.slice(1).trim();
}

function stat(label, value, note, highlight=false) {
  return `<div class="stat${highlight ? ' highlight' : ''}"><div class="stat-label">${escapeHTML(label)}</div><div class="stat-value">${escapeHTML(value)}</div><div class="stat-note">${escapeHTML(note)}</div></div>`;
}

function renderChart(rows) {
  const width=680, height=235, left=43, right=14, top=20, bottom=33;
  const ceiling=Math.ceil(Math.max(...rows.flatMap(r => [r.actual,r.model,r.baseline]),1)/50)*50;
  const x=(i)=>left+i*(width-left-right)/(rows.length-1);
  const y=(v)=>top+(1-v/ceiling)*(height-top-bottom);
  let svg=`<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="21 күндегі сұраныс, модель және өткен апта болжамының графигі"><title>Сұраныс пен болжам салыстыруы</title>`;
  for(let i=0;i<5;i++){
    const value=ceiling*i/4;
    svg+=`<line x1="${left}" y1="${y(value)}" x2="${width-right}" y2="${y(value)}" stroke="#e7dfd2"/><text x="${left-8}" y="${y(value)+4}" text-anchor="end" fill="#796c5e" font-size="10">${Math.round(value)}</text>`;
  }
  const points=(key)=>rows.map((r,i)=>`${x(i)},${y(r[key])}`).join(' ');
  svg+=`<polygon points="${left},${y(0)} ${points('actual')} ${width-right},${y(0)}" fill="#f3e6cd"/>`;
  for(const [key,color,dash] of [['actual','#b89857',''],['baseline','#8b8e79','4 5'],['model','#a34e32','']]){
    svg+=`<polyline points="${points(key)}" fill="none" stroke="${color}" stroke-width="${key==='model'?2.5:1.6}" stroke-dasharray="${dash}" stroke-linejoin="round"/>`;
  }
  for(const i of [0,5,10,15,20]){
    svg+=`<text x="${x(i)}" y="${height-10}" text-anchor="middle" fill="#796c5e" font-size="10">${rows[i].date.slice(5).replace('-','/')}</text>`;
  }
  $('#chart').innerHTML=svg+'</svg>';
}

function render(result) {
  analysis=result;
  const simulated = result.synthetic;
  const observedOnly = !simulated || result.uploaded_sample;
  $('#source-label').textContent=simulated?'ҮЛГІ ДЕРЕКТЕР':'ЖҮКТЕЛГЕН ДЕРЕКТЕР';
  $('#source-note').textContent=simulated?'Бұл — жасанды наубайхана. Нәтижелер нақты бизнес үнемін білдірмейді.':'Бағалау байқалған сатылымға сүйенеді. Өнім жетіспеген күндерде шынайы сұраныс белгісіз.';
  $('#workspace-name').replaceChildren(document.createTextNode(simulated?'Астана · демо наубайхана':'Жүктелген деректер'));
  const localLabel=document.createElement('small');localLabel.textContent='Жергілікті режим';$('#workspace-name').append(localLabel);
  $('#buffer').value=result.buffer;
  $('#buffer-value').textContent=`${result.buffer}%`;
  $('#plan-subtitle').textContent=`${dateLabel(result.next_date)} · ${result.days} күндік тарих · ${result.products.length} өнім · қолданылған қосымша қор: ${result.buffer}%`;
  const quantity=result.products.reduce((total,p)=>total+p.quantity,0);
  const demand=result.products.reduce((total,p)=>total+p.forecast,0);
  const cost=result.products.reduce((total,p)=>total+p.production_cost,0);
  $('#plan-stats').innerHTML=stat('Пісіруге ұсынылатын көлем',`${number(quantity)} дана`,'Барлық өнімдер бойынша',true)+stat('Сұраныс болжамы',`${number(demand)} дана`,'Болжам; нақты тапсырыс емес')+stat('Жоспарланған өндіріс құны',money(cost),'Өнімдердің айнымалы өзіндік құны');
  const productArt=(name)=>({ 'Круассан':'croissant','Нан':'bread','Самса':'samsa' }[name]);
  $('#products').innerHTML=result.products.map((p)=>`<tr><td><div class="product-name"><span class="product-icon" aria-hidden="true">${productArt(p.name)?`<img src="/assets/${productArt(p.name)}.svg" alt="" width="52" height="44">`:'✳'}</span><span>${escapeHTML(p.name)}<small>БАҒАСЫ ${money(p.price)}</small></span></div></td><td data-label="Сұраныс болжамы">${number(p.forecast)} дана</td><td data-label="Болжам ауқымы">${number(p.lower)}–${number(p.upper)}</td><td data-label="Пісіру ұсынысы"><span class="quantity-pill">${number(p.quantity)} дана</span></td><td data-label="Өндіріс құны">${money(p.production_cost)}</td></tr>`).join('');
  $('#product-count').textContent=`${result.products.length} өнім`;
  $('#actual-label').textContent=observedOnly?'Байқалған сатылым':'Үлгідегі сұраныс';
  renderChart(result.chart);
  $('#evaluation-period').textContent=`${dateLabel(result.evaluation_start)} — ${dateLabel(result.end_date)} · ${result.evaluation_days} күн`;
  $('#evidence-note').textContent=observedOnly?'Бұл — байқалған сатылымды сұраныстың төменгі шегі ретінде алған сценарий. Нақты жоғалған сатылым мен үнемді осы деректерден анықтау мүмкін емес.':'Жасанды сұраныс негізіндегі симуляция. Әр күннің шынайы үлгі сұранысы тек бағалауға қолданылады; модельге берілмейді.';
  const m=result.metrics.model, b=result.metrics.baseline;
  const wape=(v)=>v===null?'—':`${number(v)}%`;
  $('#evaluation-stats').innerHTML=stat('Сценарийдегі пайда айырмасы',`${result.profit_delta>=0?'+':''}${money(result.profit_delta)}`,'Israptama − өткен апта тәсілі',true)+stat('Болжам қатесі · WAPE',wape(m.wape),'Төмен мән жақсы; дәлдік пайызы емес')+stat('Сценарийдегі артық өнім',`${number(m.waste)} дана`,'Соңғы 21 күн бойынша');
  const comparison=[['Болжам қатесі · WAPE',wape(b.wape),wape(m.wape)],['Маржалық пайда · сценарий',money(b.profit),money(m.profit)],['Сатылмаған өнім · сценарий',`${number(b.waste)} дана`,`${number(m.waste)} дана`],['Өтелмеген сұраныс · сценарий',`${number(b.missed)} дана`,`${number(m.missed)} дана`]];
  $('#comparison').innerHTML=comparison.map(r=>`<tr>${r.map(c=>`<td>${escapeHTML(c)}</td>`).join('')}</tr>`).join('');
  $('#stockout-note').textContent=`Тексеріс кезеңіндегі ${result.evaluation_rows} өнім-күннің ${result.stockout_rows}-інде барлық пісірілген өнім сатылған. Мұндай күндерде сатылым сұранысты толық көрсетпеуі мүмкін.`;
  $('#dataset-summary').textContent=`${simulated?'Жасанды үлгі':'Жүктелген кесте'} · ${result.rows} жол · ${result.days} күн · ${result.products.length} өнім · ${dateLabel(result.start_date)} — ${dateLabel(result.end_date)}`;
}

function busy(value) {
  $('#loading').hidden=!value;
  for(const id of ['recalculate','download-plan','download-report','reset-sample']) $( `#${id}`).disabled=value || (id.startsWith('download')&&!analysis);
  $('#csv-file').disabled=value;
  $('#buffer').disabled=value;
}

async function requestAnalysis(csv, buffer) {
  const response=await fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({csv,buffer})});
  const body=await response.json();
  if(!response.ok) throw new Error(body.error || 'Талдау орындалмады.');
  return body;
}

async function update(csv=uploadedCSV, buffer=Number($('#buffer').value)) {
  $('#error').hidden=true;
  busy(true);
  try {
    const result=await requestAnalysis(csv,buffer);
    uploadedCSV=csv;
    render(result);
    return true;
  } catch(error) {
    $('#error').textContent=error.message;
    $('#error').hidden=false;
    return false;
  } finally { busy(false); }
}

function download(name,text,type) {
  const url=URL.createObjectURL(new Blob([text],{type}));
  const link=document.createElement('a');link.href=url;link.download=name;link.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
}

function csvCell(value) {
  let text=String(value);
  if(/^[=+\-@\t\r]/.test(text)) text="'"+text;
  return '"'+text.replaceAll('"','""')+'"';
}

document.querySelectorAll('.nav-item').forEach(button=>button.addEventListener('click',()=>showView(button.dataset.view)));
document.querySelectorAll('[data-open-view]').forEach(button=>button.addEventListener('click',()=>showView(button.dataset.openView)));
$('#buffer').addEventListener('input',()=>{$('#buffer-value').textContent=`${$('#buffer').value}%`;});
$('#recalculate').addEventListener('click',()=>update());
$('#reset-sample').addEventListener('click',async()=>{
  if(await update(null,0)){
    $('#buffer').value=0;$('#buffer-value').textContent='0%';$('#csv-file').value='';$('#file-name').textContent='Файл таңдалмады';
  }
});
$('#csv-file').addEventListener('change',async(event)=>{
  const file=event.target.files[0];if(!file)return;
  if(file.size>2_000_000){$('#error').textContent='CSV файлы 2 МБ-тан аспауы керек.';$('#error').hidden=false;event.target.value='';return;}
  try {
    const text=await file.text();
    if(await update(text)){$('#file-name').textContent=file.name;showView('plan');}
  } catch(error){$('#error').textContent=error.message;$('#error').hidden=false;}
  event.target.value='';
});
$('#download-plan').addEventListener('click',()=>{
  if(!analysis)return;
  const rows=[['source','date','product','forecast','recommended','unit_price_kzt','unit_cost_kzt','production_cost_kzt'],...analysis.products.map(p=>[analysis.synthetic?'SYNTHETIC_DEMO':'USER_UPLOADED_UNVERIFIED',analysis.next_date,p.name,p.forecast,p.quantity,p.price,p.cost,p.production_cost])];
  download(`israptama-${analysis.synthetic?'DEMO-':''}plan-${analysis.next_date}.csv`,'\ufeff'+rows.map(r=>r.map(csvCell).join(',')).join('\r\n'),'text/csv;charset=utf-8');
});
$('#download-report').addEventListener('click',()=>{
  if(!analysis)return;
  download(`israptama-${analysis.synthetic?'DEMO-':''}evaluation.json`,JSON.stringify({notice:analysis.synthetic?'SYNTHETIC SIMULATION. NOT REAL BUSINESS SAVINGS.':'OBSERVED SALES LOWER-BOUND SCENARIO. NOT VERIFIED SAVINGS.',assumptions:'No carryover or salvage. Revenue minus all variable production costs. Fixed costs excluded.',...analysis},null,2),'application/json');
});
update();
