document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. INITIALIZE MASTER STATE ---
    const dataElement = document.getElementById('init-data');
    if (!dataElement) return;
    
    let cvState = JSON.parse(dataElement.textContent);
    
    // Map to track accepted bullets and their original text for clean undo: { bulletKey: originalText }
    let acceptedBulletTracker = new Map();

    // --- 2. STEPPER LOGIC ---
    window.goToStep = function(stepNumber) {
        document.querySelectorAll('.step-container').forEach(el => el.classList.remove('active'));
        const stepEl = document.getElementById(`step-${stepNumber}`);
        if (stepEl) stepEl.classList.add('active');
        
        const progressBar = document.getElementById('progress-bar');
        if (progressBar) progressBar.style.width = `${((stepNumber - 1) / 3) * 100}%`;
        
        for (let i = 1; i <= 4; i++) {
            const ind = document.getElementById(`indicator-${i}`);
            if (!ind) continue;
            if (i < stepNumber) {
                ind.className = 'w-7 h-7 sm:w-9 sm:h-9 rounded-full bg-emerald-500 text-white font-bold flex items-center justify-center text-xs sm:text-sm ring-4 ring-white';
            } else if (i === stepNumber) {
                ind.className = 'w-7 h-7 sm:w-9 sm:h-9 rounded-full bg-indigo-600 text-white font-bold flex items-center justify-center shadow-md text-xs sm:text-sm ring-4 ring-white';
            } else {
                ind.className = 'w-7 h-7 sm:w-9 sm:h-9 rounded-full bg-slate-200 text-slate-500 font-bold flex items-center justify-center text-xs sm:text-sm ring-4 ring-white';
            }
        }

        if (stepNumber === 2) {
            renderEditor();
            renderA4();
        } else if (stepNumber === 3) {
            runATSAnalysis();
        } else if (stepNumber === 4) {
            renderA4();
            renderStep4Preview();
        }
    };

    // --- 3. TEMPLATE SELECTOR (Step 1) ---
    document.querySelectorAll('.template-card').forEach(card => {
        card.addEventListener('click', () => {
            cvState.template = card.dataset.template;
            
            if (cvState.template === 'tpl-harvard') cvState.design.color = '#000000';
            if (cvState.template === 'tpl-modern') cvState.design.color = '#2563eb';
            if (cvState.template === 'tpl-corporate') cvState.design.color = '#0f172a';
            if (cvState.template === 'tpl-creative') cvState.design.color = '#10b981';
            if (cvState.template === 'tpl-apex') cvState.design.color = '#1e293b';
            
            triggerAutoSave();
            window.goToStep(2);
        });
    });

    // --- 4. TAB CONTROLS (Step 2 Editor) ---
    window.switchTab = function(tabName) {
        const btnContent = document.getElementById('tab-btn-content');
        const btnDesign = document.getElementById('tab-btn-design');
        
        if (tabName === 'content') {
            btnContent.className = "flex-1 py-3 text-xs font-bold text-indigo-600 border-b-2 border-indigo-600 bg-white";
            btnDesign.className = "flex-1 py-3 text-xs font-bold text-slate-500 bg-slate-50 border-b border-slate-200";
            document.getElementById('tab-content').classList.remove('hidden');
            document.getElementById('tab-design').classList.add('hidden');
        } else {
            btnDesign.className = "flex-1 py-3 text-xs font-bold text-indigo-600 border-b-2 border-indigo-600 bg-white";
            btnContent.className = "flex-1 py-3 text-xs font-bold text-slate-500 bg-slate-50 border-b border-slate-200";
            document.getElementById('tab-design').classList.remove('hidden');
            document.getElementById('tab-content').classList.add('hidden');
        }
    };

    // --- 5. MODAL CONTROLS ---
    window.openAddSectionModal = () => document.getElementById('modal-add-section').classList.remove('hidden');
    window.closeModal = () => document.getElementById('modal-add-section').classList.add('hidden');

    // --- 6. DYNAMIC STATE MUTATORS ---
    window.addSection = (type, defaultTitle) => {
        const newId = 'sec-' + Date.now();
        cvState.sections.push({
            id: newId,
            type: type,
            title: defaultTitle,
            items: [{ title: 'New Entry', meta: 'Date / Info', desc: 'Description of your experience or skills.' }]
        });
        closeModal();
        renderEditor();
        renderA4();
        triggerAutoSave();
    };

    window.removeSection = (id) => {
        cvState.sections = cvState.sections.filter(s => s.id !== id);
        renderEditor();
        renderA4();
        triggerAutoSave();
    };

    window.addItem = (sectionId) => {
        const sec = cvState.sections.find(s => s.id === sectionId);
        sec.items.push({ title: 'New Entry', meta: '', desc: '' });
        renderEditor();
        renderA4();
        triggerAutoSave();
    };

    window.removeItem = (sectionId, itemIndex) => {
        const sec = cvState.sections.find(s => s.id === sectionId);
        sec.items.splice(itemIndex, 1);
        renderEditor();
        renderA4();
        triggerAutoSave();
    };

    window.updateState = (path, value) => {
        const parts = path.split('.');
        if (parts[0] === 'personal') {
            cvState.personal[parts[1]] = value;
        } else if (parts[0] === 'design') {
            cvState.design[parts[1]] = value;
            applyDesignVars();
        } else if (parts[0] === 'sections') {
            const sec = cvState.sections.find(s => s.id === parts[1]);
            if (parts[2] === 'title') sec.title = value;
            else if (parts[2] === 'items') sec.items[parts[3]][parts[4]] = value;
        }
        renderA4(); 
        triggerAutoSave();
    };

    // --- 7. BACKEND AUTO-SAVE ---
    let saveTimeout;
    window.triggerAutoSave = function() {
        const saveStatusEl = document.getElementById('save-status');
        if (saveStatusEl) {
            saveStatusEl.classList.remove('hidden');
            saveStatusEl.innerText = "Saving...";
            saveStatusEl.className = "text-[10px] font-bold text-amber-600 bg-amber-50 px-2 py-1 rounded";
        }
        
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(() => {
            fetch('/api/resume/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ resume_data: cvState })
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success' && saveStatusEl) {
                    saveStatusEl.innerText = "Saved";
                    saveStatusEl.className = "text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded";
                }
            })
            .catch(err => console.error("Autosave failed:", err));
        }, 1500);
    };

    // --- 8. EDITOR RENDER ENGINE (Left Pane) ---
    function renderEditor() {
        const nameInp = document.getElementById('inp-name');
        const contactInp = document.getElementById('inp-contact');
        if (nameInp) nameInp.value = cvState.personal.name;
        if (contactInp) contactInp.value = cvState.personal.contact;

        const container = document.getElementById('editor-sections');
        if (!container) return;
        
        let html = '';
        cvState.sections.forEach((sec) => {
            html += `
            <div class="mb-6 bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
                <div class="bg-slate-50 p-3 flex justify-between items-center border-b border-slate-200">
                    <input type="text" value="${sec.title}" oninput="updateState('sections.${sec.id}.title', this.value)" class="text-sm font-bold text-slate-800 bg-transparent border-none focus:ring-0 p-0 w-3/4 uppercase">
                    <button onclick="removeSection('${sec.id}')" class="text-slate-400 hover:text-red-500 hover:bg-red-50 p-1 rounded transition" title="Delete Section">🗑️</button>
                </div>
                <div class="p-4 space-y-4">
            `;

            if (sec.type === 'text') {
                html += `<textarea oninput="updateState('sections.${sec.id}.items.0.desc', this.value)" class="w-full p-2.5 text-sm border border-slate-300 rounded-lg h-24 font-mono text-xs">${sec.items[0].desc}</textarea>`;
            } else if (sec.type === 'list') {
                sec.items.forEach((item, iIdx) => {
                    html += `
                    <div class="relative bg-slate-50 p-3 border border-slate-200 rounded-lg mb-3 group">
                        <button onclick="removeItem('${sec.id}', ${iIdx})" class="absolute top-2 right-2 text-slate-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition" title="Delete Entry">✕</button>
                        <div class="flex gap-2 mb-2 pr-6">
                            <input type="text" oninput="updateState('sections.${sec.id}.items.${iIdx}.title', this.value)" value="${item.title}" class="flex-1 p-2 text-sm font-bold border border-slate-300 rounded focus:ring-1 focus:ring-indigo-500" placeholder="Title">
                            <input type="text" oninput="updateState('sections.${sec.id}.items.${iIdx}.meta', this.value)" value="${item.meta}" class="w-1/3 p-2 text-sm border border-slate-300 rounded focus:ring-1 focus:ring-indigo-500" placeholder="Date/Meta">
                        </div>
                        <textarea oninput="updateState('sections.${sec.id}.items.${iIdx}.desc', this.value)" class="w-full p-2 text-xs border border-slate-300 rounded h-16 font-mono" placeholder="Bullet description...">${item.desc}</textarea>
                    </div>`;
                });
                html += `<button onclick="addItem('${sec.id}')" class="text-xs font-bold text-indigo-600 mt-1 flex items-center gap-1 hover:text-indigo-800 transition">+ Add New Entry</button>`;
            }
            html += `</div></div>`;
        });
        container.innerHTML = html;
        
        const ids = ['color', 'font', 'size', 'lineStyle', 'lineThickness', 'align'];
        ids.forEach(id => {
            const el = document.getElementById(`design-${id}`);
            if (el) el.value = cvState.design[id];
        });
    }

    // --- 9. A4 PREVIEW RENDER ENGINE (Right Pane & Live Canvas) ---
    function renderA4() {
        const canvas = document.getElementById('live-a4-canvas');
        if (!canvas) return;
        
        canvas.className = `a4-blueprint ${cvState.template}`; 

        let html = `
            <div class="cv-header">
                <div class="cv-name">${cvState.personal.name}</div>
                <div class="cv-contact">${cvState.personal.contact}</div>
            </div>
        `;

        cvState.sections.forEach(sec => {
            html += `<div class="cv-section"><div class="cv-section-title">${sec.title}</div>`;
            
            if (sec.type === 'text') {
                const formattedDesc = (sec.items[0]?.desc || '').replace(/\n/g, '<br>');
                html += `<div class="cv-item-desc" style="list-style:none; margin-left:0;">${formattedDesc}</div>`;
            } else {
                sec.items.forEach(item => {
                    let formattedDesc = item.desc || '';
                    if (formattedDesc.includes('\n')) {
                        formattedDesc = formattedDesc.split('\n')
                            .map(line => line.trim())
                            .filter(line => line.length > 0)
                            .map(line => `<li>${line.replace(/^[•\-\*]\s*/, '')}</li>`)
                            .join('');
                        formattedDesc = `<ul>${formattedDesc}</ul>`;
                    } else if (formattedDesc.trim()) {
                        formattedDesc = `<ul><li>${formattedDesc.trim().replace(/^[•\-\*]\s*/, '')}</li></ul>`;
                    }

                    html += `
                    <div class="cv-item">
                        <div class="cv-item-header">
                            <div class="cv-item-title">${item.title}</div>
                            <div class="cv-item-meta">${item.meta}</div>
                        </div>
                        <div class="cv-item-desc">${formattedDesc}</div>
                    </div>`;
                });
            }
            html += `</div>`;
        });

        canvas.innerHTML = html;
        applyDesignVars();
    }

    function applyDesignVars() {
        const root = document.getElementById('live-a4-canvas');
        if (!root) return;
        root.style.setProperty('--cv-theme-color', cvState.design.color);
        root.style.setProperty('--cv-font-base', cvState.design.font);
        root.style.setProperty('--cv-text-size', `${cvState.design.size}pt`);
        root.style.setProperty('--cv-line-style', cvState.design.lineStyle);
        root.style.setProperty('--cv-line-thickness', `${cvState.design.lineThickness}px`);
        root.style.setProperty('--cv-header-align', cvState.design.align);
    }

    // --- 10. STEP 3: ATOMIC AI COPILOT & STATE PERSISTENCE ---
    let currentParsedBullets = [];

    window.calculateScoreValues = function() {
        let score = 100;
        let feedback = [];
        let totalWords = 0;
        let actionVerbCount = 0;
        let metricCount = 0;

        const strongVerbs = ['engineered', 'developed', 'spearheaded', 'managed', 'created', 'led', 'analyzed', 'optimized', 'designed', 'implemented', 'built', 'formulated', 'orchestrated'];

        cvState.sections.forEach(sec => {
            if (sec.type === 'list') {
                sec.items.forEach(item => {
                    const desc = item.desc ? item.desc.trim() : "";
                    if (desc) {
                        const words = desc.split(/\s+/).filter(Boolean);
                        totalWords += words.length;
                        if (/\d+%|\d+/.test(desc)) metricCount++;
                        if (strongVerbs.some(v => desc.toLowerCase().includes(v))) actionVerbCount++;
                    }
                });
            } else if (sec.type === 'text') {
                const desc = sec.items[0]?.desc ? sec.items[0].desc.trim() : "";
                if (desc) totalWords += desc.split(/\s+/).filter(Boolean).length;
            }
        });

        if (totalWords < 80) { 
            score -= 25; 
            feedback.push("❌ Resume is too brief. Add more technical details to your experience and projects."); 
        } else { 
            feedback.push("✅ Professional word count achieved."); 
        }

        if (metricCount < 1) { 
            score -= 25; 
            feedback.push("❌ Missing metrics. Use numbers or percentages in your project descriptions."); 
        } else { 
            feedback.push(`✅ Found ${metricCount} quantified metrics.`); 
        }

        if (actionVerbCount < 2) { 
            score -= 20; 
            feedback.push("❌ Weak vocabulary. Start bullet points with strong action verbs (e.g., 'Engineered', 'Formulated')."); 
        } else { 
            feedback.push("✅ Strong action verb density detected."); 
        }

        return {
            finalScore: Math.max(score, 30),
            feedback: feedback
        };
    };

    window.updateScoreUIOnly = function() {
        const stats = calculateScoreValues();
        const scoreCircle = document.getElementById('ats-score-circle');
        const feedbackList = document.getElementById('ats-feedback-list');

        if (scoreCircle) {
            scoreCircle.innerText = stats.finalScore;
            scoreCircle.className = `w-24 h-24 rounded-full flex items-center justify-center text-3xl font-black text-white shadow-lg mx-auto ${stats.finalScore >= 80 ? 'bg-emerald-500' : stats.finalScore >= 60 ? 'bg-amber-500' : 'bg-red-500'}`;
        }

        if (feedbackList) {
            feedbackList.innerHTML = stats.feedback.map(f => `<div class="text-xs font-semibold text-slate-600 mb-2 p-3 bg-slate-50 rounded-lg border border-slate-200">${f}</div>`).join('');
        }
    };

    window.runATSAnalysis = function() {
        updateScoreUIOnly();
        currentParsedBullets = [];

        cvState.sections.forEach(sec => {
            if (sec.type === 'list') {
                sec.items.forEach((item, itemIdx) => {
                    const rawDesc = item.desc ? item.desc.trim() : "";
                    if (!rawDesc) return;

                    const lines = rawDesc.split('\n')
                        .map(l => l.trim().replace(/^[•\-\*]\s*/, ''))
                        .filter(l => l.length > 5);

                    lines.forEach((lineText, lineIdx) => {
                        if (!lineText.toLowerCase().includes('university') && !lineText.toLowerCase().includes('college')) {
                            const bulletKey = `${sec.id}_${itemIdx}_${lineIdx}`;
                            const isAccepted = acceptedBulletTracker.has(bulletKey);

                            currentParsedBullets.push({
                                key: bulletKey,
                                secId: sec.id,
                                secTitle: sec.title || "Section",
                                itemIdx: itemIdx,
                                entryTitle: item.title || "General Entry",
                                lineIdx: lineIdx,
                                text: lineText,
                                isAccepted: isAccepted
                            });
                        }
                    });
                });
            }
        });

        renderAIImproverCards();
    };

    function renderAIImproverCards() {
        const improverList = document.getElementById('ai-improver-list');
        if (!improverList) return;

        if (currentParsedBullets.length === 0) {
            improverList.innerHTML = "<p class='text-sm text-slate-500 italic p-4 bg-slate-50 rounded-xl'>Add detailed project bullet points in Step 2 to unlock AI rewrites.</p>";
            return;
        }

        improverList.innerHTML = currentParsedBullets.map((b, idx) => `
            <div class="bg-white p-5 border border-slate-200 rounded-xl mb-4 shadow-sm transition-all" id="bullet-container-${idx}">
                <div class="flex items-center justify-between mb-2 pb-2 border-b border-slate-100">
                    <div class="flex items-center gap-2">
                        <span class="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-100">${b.secTitle}</span>
                        <span class="text-xs font-bold text-slate-700">› ${b.entryTitle}</span>
                    </div>
                    <span id="badge-status-${idx}" class="text-[10px] font-bold ${b.isAccepted ? 'text-emerald-700 bg-emerald-50 border border-emerald-200' : 'text-slate-500 bg-slate-100'} px-2 py-0.5 rounded">
                        ${b.isAccepted ? 'Accepted ✓' : 'Ready'}
                    </span>
                </div>
                <p class="text-xs font-mono text-slate-700 mb-3 bg-slate-50 p-3 rounded-lg border border-slate-100" id="bullet-text-${idx}">${b.text}</p>
                <div id="ai-result-${idx}" class="hidden mb-3 p-3 bg-indigo-50 border border-indigo-200 rounded-lg text-xs font-semibold text-indigo-900 leading-relaxed"></div>
                <div class="flex gap-2 items-center" id="action-container-${idx}">
                    ${b.isAccepted ? `
                        <span class="text-xs font-bold text-emerald-700 flex items-center gap-1.5 py-1.5 px-3 bg-emerald-50 rounded-lg border border-emerald-200">
                            ✓ Applied to Resume
                        </span>
                        <button onclick="undoImprovement(${idx})" class="text-xs font-semibold text-rose-500 hover:text-rose-700 transition ml-3 flex items-center gap-1">
                            ↺ Undo & Restore Original
                        </button>
                    ` : `
                        <button onclick="improveBullet(${idx})" id="btn-improve-${idx}" class="text-xs font-bold bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition shadow-sm flex items-center gap-1.5">✨ AI Improve</button>
                        <button onclick="acceptImprovement(${idx})" id="btn-accept-${idx}" class="hidden text-xs font-bold bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700 transition shadow-sm">Accept Change</button>
                        <button onclick="dismissImprovement(${idx})" id="btn-dismiss-${idx}" class="hidden text-xs font-semibold text-slate-500 hover:text-slate-700 px-3 py-2 transition">Dismiss</button>
                    `}
                </div>
            </div>
        `).join('');
    }

    window.improveBullet = function(idx) {
        const bulletMeta = currentParsedBullets[idx];
        if (!bulletMeta) return;

        const btnImprove = document.getElementById(`btn-improve-${idx}`);
        const btnAccept = document.getElementById(`btn-accept-${idx}`);
        const btnDismiss = document.getElementById(`btn-dismiss-${idx}`);
        const resultBox = document.getElementById(`ai-result-${idx}`);
        const badge = document.getElementById(`badge-status-${idx}`);
        
        btnImprove.innerText = "⏳ Generating...";
        btnImprove.disabled = true;

        fetch('/api/resume/improve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                text: bulletMeta.text, 
                section_title: bulletMeta.secTitle,
                entry_title: bulletMeta.entryTitle,
                target_role: cvState.personal.name || ""
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                resultBox.innerText = data.improved_text;
                resultBox.classList.remove('hidden');
                
                btnImprove.classList.add('hidden');
                btnImprove.innerText = "✨ AI Improve";
                btnImprove.disabled = false;
                
                btnAccept.classList.remove('hidden');
                btnAccept.dataset.newText = data.improved_text;
                btnDismiss.classList.remove('hidden');

                if (badge) {
                    badge.innerText = "Suggestion Available";
                    badge.className = "text-[10px] font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100";
                }
            } else {
                throw new Error(data.message || "Failed to generate");
            }
        })
        .catch(err => {
            console.error("AI Error:", err);
            btnImprove.innerText = "Failed. Try again.";
            btnImprove.disabled = false;
            if (badge) {
                badge.innerText = "Error";
                badge.className = "text-[10px] font-bold text-red-700 bg-red-50 px-2 py-0.5 rounded";
            }
        });
    };

    window.dismissImprovement = function(idx) {
        const btnImprove = document.getElementById(`btn-improve-${idx}`);
        const btnAccept = document.getElementById(`btn-accept-${idx}`);
        const btnDismiss = document.getElementById(`btn-dismiss-${idx}`);
        const resultBox = document.getElementById(`ai-result-${idx}`);
        const badge = document.getElementById(`badge-status-${idx}`);

        if (resultBox) {
            resultBox.innerText = "";
            resultBox.classList.add('hidden');
        }
        if (btnAccept) btnAccept.classList.add('hidden');
        if (btnDismiss) btnDismiss.classList.add('hidden');
        if (btnImprove) btnImprove.classList.remove('hidden');

        if (badge) {
            badge.innerText = "Ready";
            badge.className = "text-[10px] font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded";
        }
    };

    window.acceptImprovement = function(idx) {
        const bulletMeta = currentParsedBullets[idx];
        const acceptBtn = document.getElementById(`btn-accept-${idx}`);
        const resultBox = document.getElementById(`ai-result-${idx}`);
        const bulletTextEl = document.getElementById(`bullet-text-${idx}`);
        
        if (!bulletMeta || !acceptBtn || !resultBox || !bulletTextEl) return;
        const newText = acceptBtn.dataset.newText;
        if (!newText) return;

        const sec = cvState.sections.find(s => s.id === bulletMeta.secId);
        if (!sec || !sec.items[bulletMeta.itemIdx]) return;

        // 1. Capture the EXACT original sentence prior to replacement
        const rawDesc = sec.items[bulletMeta.itemIdx].desc || "";
        let lines = rawDesc.split('\n');

        // Store the original line value mapped to this unique bullet key
        const originalLineText = lines[bulletMeta.lineIdx] || bulletMeta.text;
        acceptedBulletTracker.set(bulletMeta.key, originalLineText);

        // 2. Perform the replacement in state
        if (lines.length > bulletMeta.lineIdx) {
            lines[bulletMeta.lineIdx] = newText;
        } else {
            lines.push(newText);
        }
        sec.items[bulletMeta.itemIdx].desc = lines.join('\n');

        // 3. Mark as accepted in local tracking
        bulletMeta.text = newText;
        bulletMeta.isAccepted = true;

        // 4. Update UI Card in place
        bulletTextEl.innerText = newText;
        resultBox.innerText = "";
        resultBox.classList.add('hidden');

        const actionContainer = document.getElementById(`action-container-${idx}`);
        if (actionContainer) {
            actionContainer.innerHTML = `
                <span class="text-xs font-bold text-emerald-700 flex items-center gap-1.5 py-1.5 px-3 bg-emerald-50 rounded-lg border border-emerald-200">
                    ✓ Applied to Resume
                </span>
                <button onclick="undoImprovement(${idx})" class="text-xs font-semibold text-rose-500 hover:text-rose-700 transition ml-3 flex items-center gap-1">
                    ↺ Undo & Restore Original
                </button>
            `;
        }

        const badge = document.getElementById(`badge-status-${idx}`);
        if (badge) {
            badge.innerText = "Accepted ✓";
            badge.className = "text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200";
        }

        // 5. Force full re-render across Step 2 editor, live A4, and Step 4 export preview
        renderEditor();
        renderA4();
        renderStep4Preview();
        updateScoreUIOnly();
        triggerAutoSave();
    };

    window.undoImprovement = function(idx) {
        const bulletMeta = currentParsedBullets[idx];
        if (!bulletMeta) return;

        const originalText = acceptedBulletTracker.get(bulletMeta.key);
        if (!originalText) return;

        const sec = cvState.sections.find(s => s.id === bulletMeta.secId);
        if (sec && sec.items[bulletMeta.itemIdx]) {
            let rawDesc = sec.items[bulletMeta.itemIdx].desc || "";
            let lines = rawDesc.split('\n');

            // Swap back the exact previous sentence into cvState
            if (lines.length > bulletMeta.lineIdx) {
                lines[bulletMeta.lineIdx] = originalText;
            } else {
                lines = [originalText];
            }
            sec.items[bulletMeta.itemIdx].desc = lines.join('\n');
        }

        // Clear tracking cache
        acceptedBulletTracker.delete(bulletMeta.key);
        bulletMeta.text = originalText;
        bulletMeta.isAccepted = false;

        // Re-render AI reviewer cards so it resets back to "Ready" state with the "✨ AI Improve" button
        renderAIImproverCards();

        // Immediately purge the accepted change from the actual live resume
        renderEditor();
        renderA4();
        renderStep4Preview();
        updateScoreUIOnly();
        triggerAutoSave();
    };

    // --- 11. STEP 4: PREVIEW SYNCHRONIZATION ---
    function renderStep4Preview() {
        const liveCanvas = document.getElementById('live-a4-canvas');
        const exportContainer = document.getElementById('export-a4-preview');
        if (liveCanvas && exportContainer) {
            exportContainer.innerHTML = liveCanvas.outerHTML;
            const innerDoc = exportContainer.querySelector('#live-a4-canvas');
            if (innerDoc) {
                innerDoc.id = "export-rendered-doc";
                innerDoc.style.transform = "scale(0.85)";
                innerDoc.style.transformOrigin = "top center";
                innerDoc.style.margin = "0 auto";
            }
        }
    }

    window.downloadPDF = function() {
        document.querySelectorAll('.step-container').forEach(el => el.classList.remove('active'));
        document.getElementById('step-2').classList.add('active');
        
        setTimeout(() => {
            window.print();
            window.goToStep(4);
        }, 100);
    };
});