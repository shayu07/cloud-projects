const API='';
let debounceTimer;

async function checkData(){
    const fd=getFormData();
    if(!fd.name||!fd.email||!fd.phone){showToast('Patient name, email, and phone are required.','error');return}
    const btn=document.getElementById('btnCheck');
    btn.textContent='⏳ Verifying...';btn.disabled=true;
    try{
        const res=await fetch(`${API}/api/check`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(fd)});
        const data=await res.json();
        showResult(data,fd);
    }catch(e){showToast('Error: '+e.message,'error')}
    finally{btn.textContent='🔍 Verify & Check Duplicates';btn.disabled=false}
}

function getFormData(){
    return {
        name:document.getElementById('inputName').value.trim(),
        email:document.getElementById('inputEmail').value.trim(),
        phone:document.getElementById('inputPhone').value.trim(),
        age:document.getElementById('inputAge').value.trim(),
        gender:document.getElementById('inputGender').value,
        blood_group:document.getElementById('inputBlood').value,
        address:document.getElementById('inputAddress').value.trim()
    };
}

function showResult(r,fd){
    const panel=document.getElementById('resultPanel'),content=document.getElementById('resultContent'),actions=document.getElementById('resultActions');
    panel.classList.remove('hidden');
    if(r.is_duplicate){
        const matchText = r.matched_fields && r.matched_fields.length ? `(Matched on: ${r.matched_fields.join(', ')})` : '';
        if(r.match_type==='EXACT'){
            content.innerHTML=`<div class="result-badge danger">🚫 DUPLICATE PATIENT FOUND</div><p>${r.message} <br><small>${matchText}</small></p><div class="match-info"><strong>Existing Patient:</strong> ${r.matched_record.name} | ${r.matched_record.phone} | ${r.matched_record.blood_group||'N/A'}</div><div class="confidence-bar"><div class="confidence-fill danger" style="width:100%">100% Match</div></div>`;
            actions.innerHTML=`<button class="btn btn-danger" disabled>❌ Registration Blocked — Patient Already Exists</button>`;
            addLog('BLOCKED: Duplicate patient — '+fd.name+' ('+fd.phone+')','danger');
        }else{
            content.innerHTML=`<div class="result-badge warning">⚠️ SIMILAR PATIENT FOUND (${r.confidence}%)</div><p>${r.message} <br><small>${matchText}</small></p><div class="match-info"><strong>Similar Patient:</strong> ${r.matched_record.name} | ${r.matched_record.phone} | ${r.matched_record.blood_group||'N/A'}</div><div class="confidence-bar"><div class="confidence-fill warning" style="width:${r.confidence}%">${r.confidence}%</div></div>`;
            actions.innerHTML=`<button class="btn btn-success" onclick='forceAdd(${JSON.stringify(fd)})'>✅ Different Patient — Register Anyway</button><button class="btn btn-outline" onclick="dismissResult()">❌ Cancel</button>`;
            addLog('WARNING: Similar patient found ('+r.confidence+'%) — '+fd.name,'warning');
        }
    }else{
        const isCloudConnected = document.getElementById('cloudStatus').innerText.includes('AWS');
        const btnText = isCloudConnected ? '✅ Register Patient & Sync to Cloud' : '✅ Register Patient (Local Only)';
        content.innerHTML=`<div class="result-badge success">✅ NO DUPLICATE — UNIQUE PATIENT</div><p>${r.message}</p><div class="confidence-bar"><div class="confidence-fill success" style="width:100%">Verified Unique</div></div>`;
        actions.innerHTML=`<button class="btn btn-success" onclick='addRecord(${JSON.stringify(fd)})'>${btnText}</button>`;
        addLog('VERIFIED: Unique patient — '+fd.name,'success');
    }
}

async function addRecord(fd){
    try{
        const res=await fetch(`${API}/api/add`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(fd)});
        const d=await res.json();
        if(res.status===409){showToast('Blocked!','error');addLog('BLOCKED: '+d.message,'danger')}
        else{showToast(`Patient #${d.record_id} registered! ${d.cloud_sync.message}`,'success');addLog(`REGISTERED: Patient #${d.record_id} — ${fd.name} — ${d.cloud_sync.message}`,'success');clearForm();loadRecords();loadStats()}
    }catch(e){showToast('Error: '+e.message,'error')}
}

async function forceAdd(fd){
    try{
        const res=await fetch(`${API}/api/force-add`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(fd)});
        const d=await res.json();
        showToast(`Patient #${d.record_id} registered (override)!`,'success');
        addLog(`OVERRIDE: Patient #${d.record_id} — ${fd.name}`,'warning');
        clearForm();loadRecords();loadStats();
    }catch(e){showToast('Error: '+e.message,'error')}
}

let allRecordsCache = []; // Store records to access for editing

function editRecord(id) {
    const record = allRecordsCache.find(r => r.id === id);
    if(!record) return;
    
    document.getElementById('editId').value = record.id;
    document.getElementById('editName').value = record.name;
    document.getElementById('editEmail').value = record.email;
    document.getElementById('editPhone').value = record.phone;
    document.getElementById('editAge').value = record.age || '';
    document.getElementById('editGender').value = record.gender || '';
    document.getElementById('editBlood').value = record.blood_group || '';
    document.getElementById('editAddress').value = record.address || '';
    
    document.getElementById('editModal').classList.remove('hidden');
}

function closeEditModal() {
    document.getElementById('editModal').classList.add('hidden');
}

async function submitEdit() {
    const id = document.getElementById('editId').value;
    const fd = {
        name: document.getElementById('editName').value.trim(),
        email: document.getElementById('editEmail').value.trim(),
        phone: document.getElementById('editPhone').value.trim(),
        age: document.getElementById('editAge').value.trim(),
        gender: document.getElementById('editGender').value,
        blood_group: document.getElementById('editBlood').value,
        address: document.getElementById('editAddress').value.trim()
    };
    
    if(!fd.name || !fd.email || !fd.phone) {
        showToast('Name, Email, and Phone are required.', 'error');
        return;
    }
    
    try {
        const res = await fetch(`${API}/api/records/${id}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(fd)
        });
        const d = await res.json();
        if(res.status === 400) { showToast(d.error, 'error'); return; }
        
        showToast(d.message, 'success');
        addLog(`UPDATED: Patient #${id} — ${fd.name}`, 'info');
        closeEditModal();
        loadRecords();
        loadStats();
    } catch(e) {
        showToast('Failed to update patient.', 'error');
    }
}

async function deleteRecord(id){
    if(!confirm(`⚠️ WARNING: Are you sure you want to permanently delete Patient #${id} from the database? This cannot be undone.`))return;
    try{await fetch(`${API}/api/records/${id}`,{method:'DELETE'});showToast(`Patient #${id} removed.`,'info');addLog(`REMOVED: Patient #${id}`,'danger');loadRecords();loadStats()}catch(e){showToast('Error','error')}
}

function searchRecords(){
    clearTimeout(debounceTimer);
    debounceTimer=setTimeout(()=>loadRecords(document.getElementById('searchInput').value),300);
}

async function loadRecords(q=''){
    try{
        const url=q?`${API}/api/records?q=${encodeURIComponent(q)}`:`${API}/api/records`;
        const res=await fetch(url);const d=await res.json();
        const tb=document.getElementById('recordsBody');
        document.getElementById('tableBadge').textContent = d.records.length;
        allRecordsCache = d.records;
        
        if(d.records.length===0){tb.innerHTML='<tr><td colspan="8" class="empty-state">No patients found.</td></tr>';return}
        tb.innerHTML=d.records.map((r, index)=>`<tr>
            <td><span class="id-badge">#${d.records.length - index}</span></td>
            <td><strong>${r.name}</strong><br><span class="sub">${r.email}</span></td>
            <td>${r.age||'—'}</td><td>${r.gender||'—'}</td>
            <td><span class="blood-badge">${r.blood_group||'—'}</span></td>
            <td>${r.phone}</td>
            <td>${r.cloud_synced?'<span class="cloud-yes" title="Synced to AWS">☁️</span>':'<span class="sub" title="Local Only">⏳</span>'}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-edit" onclick="editRecord(${r.id})" title="Edit Patient">✏️</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteRecord(${r.id})" title="Delete Patient">🗑️</button>
                </div>
            </td>
        </tr>`).join('');
    }catch(e){console.error(e)}
}

async function loadStats(){
    try{
        const res=await fetch(`${API}/api/stats`);const d=await res.json();
        document.getElementById('statTotal').textContent=d.total_records;
        document.getElementById('statDuplicates').textContent=d.duplicates_caught;
        document.getElementById('statAccuracy').textContent=d.accuracy+'%';
        
        const s=document.getElementById('cloudStatus');
        const warning = document.getElementById('localWarningBanner');
        const syncStat = document.getElementById('statCloudSync');
        
        if (d.cloud.connected) {
            s.innerHTML = `<span class="status-dot connected"></span><span class="status-text">AWS S3 — ${d.cloud.region}</span>`;
            warning.classList.add('hidden');
            syncStat.textContent = d.cloud_synced;
            syncStat.style.fontSize = '1.8rem';
        } else {
            s.innerHTML = `<span class="status-dot local"></span><span class="status-text">Local Mode</span>`;
            warning.classList.remove('hidden');
            syncStat.textContent = 'Not Configured';
            syncStat.style.fontSize = '1.2rem';
        }
    }catch(e){console.error(e)}
}

async function triggerBackup(){
    showToast('Backing up to AWS S3...','info');
    try{const res=await fetch(`${API}/api/cloud/backup`,{method:'POST'});const d=await res.json();showToast(d.message,d.status==='uploaded'?'success':'info');addLog('BACKUP: '+d.message,d.status==='uploaded'?'success':'info')}catch(e){showToast('Failed','error')}
}

function clearForm(){document.getElementById('dataForm').reset();dismissResult()}
function dismissResult(){document.getElementById('resultPanel').classList.add('hidden')}
function addLog(msg,type='info'){const log=document.getElementById('logEntries');const t=new Date().toLocaleTimeString();const el=document.createElement('div');el.className=`log-entry ${type}`;el.innerHTML=`<span class="log-time">[${t}]</span> ${msg}`;log.prepend(el)}
function clearLog(){document.getElementById('logEntries').innerHTML='<div class="log-entry info">Log cleared.</div>'}
function showToast(msg,type='info'){const c=document.getElementById('toastContainer');const t=document.createElement('div');t.className=`toast ${type}`;t.textContent=msg;c.appendChild(t);setTimeout(()=>t.classList.add('show'),10);setTimeout(()=>{t.classList.remove('show');setTimeout(()=>t.remove(),300)},3500)}
function updateTime(){const now=new Date();document.getElementById('headerTime').textContent=now.toLocaleString('en-IN',{weekday:'short',day:'numeric',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit'})}

updateTime();setInterval(updateTime,60000);
loadRecords();loadStats();
