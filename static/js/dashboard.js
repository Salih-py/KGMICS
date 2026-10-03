document.addEventListener('DOMContentLoaded', () => {
    const suggestBtn = document.getElementById('suggest-btn');
    const bioTextarea = document.getElementById('bio-textarea');
    const suggestPhraseBtn = document.getElementById('suggest-phrase-btn');

    const loadingState = document.getElementById('loading-state');
    const recsSection = document.getElementById('recs-section');
    const recsContainer = document.getElementById('recs-container');
    const metricsSection = document.getElementById('metrics-section');
    const nlpSummaryCard = document.getElementById('nlp-summary-card');
    const nlpSkillsTags = document.getElementById('nlp-skills-tags');

    // Autofill Template Button
    if (suggestPhraseBtn) {
        suggestPhraseBtn.addEventListener('click', () => {
            const template = `Hello, my name is Anu. I am currently doing my B.A. Social Science with Economics as my main area. I have worked on college projects involving basic economic research, data collection, surveys, Excel/spreadsheets, and data analysis. I'm interested in microeconomics, development economics, public policy, social research, statistics, and understanding how markets and society affect each other. I have used MS Excel, Google Sheets, PowerPoint and am familiar with SPSS, basic Python, and research/report writing. Looking for entry-level opportunities where I can learn more about economics, research, and policy-related work.`;
            bioTextarea.value = template;
            bioTextarea.focus();
        });
    }

    // Submit handler
    if (suggestBtn) {
        suggestBtn.addEventListener('click', async () => {
            const bioText = bioTextarea.value.trim();

            // Hide old results
            recsSection.classList.add('hidden');
            metricsSection.classList.add('hidden');
            if (nlpSummaryCard) nlpSummaryCard.classList.add('hidden');
            
            // Show loading animation
            loadingState.classList.remove('hidden');
            
            // Disable button and show spinner to prevent duplicate clicks
            suggestBtn.disabled = true;
            const btnText = document.getElementById('btn-text');
            const btnSpinner = document.getElementById('btn-spinner');
            if (btnSpinner) btnSpinner.classList.remove('hidden');
            if (btnText) btnText.textContent = "Running Analysis...";

            try {
                // Fetch from the backend with a minimum 750ms animation delay for smooth UI
                const [response] = await Promise.all([
                    fetch('/api/suggest_career', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ bio_text: bioText })
                    }),
                    new Promise(res => setTimeout(res, 750))
                ]);

                const data = await response.json();

                if (data.status === 'success') {
                    // 1. Render NLP Extracted Skills Summary Banner
                    if (nlpSummaryCard && nlpSkillsTags) {
                        let tagsHtml = '';
                        
                        // Render standard taxonomy skills in Green
                        if (data.extracted_skills && data.extracted_skills.length > 0) {
                            tagsHtml += data.extracted_skills
                                .map(s => `<span class="px-2.5 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-semibold rounded-lg shadow-sm">✓ ${s}</span>`)
                                .join('');
                        }
                        
                        // FORWARD LOGIC: Render Novel/Outside-mapping skills in Blue!
                        if (data.novel_skills && data.novel_skills.length > 0) {
                            tagsHtml += data.novel_skills
                                .map(s => `<span class="px-2.5 py-1 bg-blue-50 text-blue-700 border border-blue-200 text-xs font-semibold rounded-lg shadow-sm">✨ ${s}</span>`)
                                .join('');
                        }

                        if (tagsHtml === '') {
                            nlpSkillsTags.innerHTML = `<span class="text-xs text-slate-400 italic">No specific technical domain skills detected.</span>`;
                        } else {
                            nlpSkillsTags.innerHTML = tagsHtml;
                        }
                        nlpSummaryCard.classList.remove('hidden');
                    }

                    // 2. Update the 6 Paper Evaluation Metrics
                    const m = data.metrics;
                    if (m) {
                        document.getElementById('m-acc').textContent = m.acc + '%';
                        document.getElementById('m-auc').textContent = m.auc;
                        document.getElementById('m-f1').textContent = m.f1;
                        document.getElementById('m-ndcg').textContent = m.ndcg;
                        document.getElementById('m-prec').textContent = m.precision;
                        document.getElementById('m-rec').textContent = m.recall;
                    }

                    // 3. Render Ranked Career Cards
                    renderCareerCards(data.recommendations);

                    // Reveal sections and hide loader
                    loadingState.classList.add('hidden');
                    recsSection.classList.remove('hidden');
                    metricsSection.classList.remove('hidden');

                    // Smooth scroll to the results
                    recsSection.scrollIntoView({ behavior: 'smooth' });
                    
                } else if (data.status === 'error') {
                    // Handled error (e.g. bio too short or low signal gibberish)
                    alert(data.message);
                    loadingState.classList.add('hidden');
                } else {
                    // Unknown error
                    alert("Analysis error. Please try again.");
                    loadingState.classList.add('hidden');
                }
            } catch (err) {
                console.error(err);
                alert("Network error connecting to recommendation engine.");
                loadingState.classList.add('hidden');
            } finally {
                // CRITICAL FIX: ALWAYS reset the button state so it never gets stuck
                if (btnText) btnText.textContent = "Run KGIMCS Career Analysis";
                if (btnSpinner) btnSpinner.classList.add('hidden');
                suggestBtn.disabled = false;
            }
        });
    }

    function renderCareerCards(recs) {
        if (!recs || recs.length === 0) return;

        const hero = recs[0];
        const gridItems = recs.slice(1, 5);

        // --- Build Hero Card Skills Section ---
        let heroMatchedHtml = '';
        if (hero.matched_skills && hero.matched_skills.length > 0) {
            heroMatchedHtml = `
                <div>
                    <span class="text-[11px] font-bold text-emerald-400 uppercase tracking-wide">✓ Identified from Your Bio:</span>
                    <div class="flex flex-wrap gap-1.5 mt-1.5">
                        ${hero.matched_skills.map(s => `<span class="px-2.5 py-1 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-lg text-xs font-semibold">✓ ${s}</span>`).join('')}
                    </div>
                </div>
            `;
        }

        let heroMissingHtml = '';
        if (hero.missing_skills && hero.missing_skills.length > 0) {
            heroMissingHtml = `
                <div class="mt-3">
                    <span class="text-[11px] font-bold text-amber-400 uppercase tracking-wide">+ Missing Prerequisite Skills:</span>
                    <div class="flex flex-wrap gap-1.5 mt-1.5">
                        ${hero.missing_skills.map(s => `<span class="px-2.5 py-1 bg-amber-400/20 text-amber-300 border border-amber-400/30 rounded-lg text-xs font-semibold">+ ${s}</span>`).join('')}
                    </div>
                </div>
            `;
        }

        // --- Build Grid Cards (Ranks 2 to 5) ---
        let gridHtml = '';
        gridItems.forEach((rec, idx) => {
            let matchedHtml = '';
            if (rec.matched_skills && rec.matched_skills.length > 0) {
                matchedHtml = `
                    <div class="mt-4 pt-3 border-t border-slate-100">
                        <p class="text-[11px] font-bold text-emerald-700 uppercase tracking-wide">✓ Identified Skills:</p>
                        <div class="flex flex-wrap gap-1.5 mt-1.5">
                            ${rec.matched_skills.map(s => `<span class="px-2 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded text-xs font-semibold">✓ ${s}</span>`).join('')}
                        </div>
                    </div>
                `;
            }

            let missingHtml = '';
            if (rec.missing_skills && rec.missing_skills.length > 0) {
                missingHtml = `
                    <div class="mt-3 pt-3 border-t border-slate-100">
                        <p class="text-[11px] font-bold text-amber-700 uppercase tracking-wide">+ Missing Skills:</p>
                        <div class="flex flex-wrap gap-1.5 mt-1.5">
                            ${rec.missing_skills.map(s => `<span class="px-2 py-0.5 bg-amber-50 text-amber-700 border border-amber-200 rounded text-xs font-semibold">+ ${s}</span>`).join('')}
                        </div>
                    </div>
                `;
            }

            gridHtml += `
                <div class="bg-white p-6 sm:p-7 rounded-3xl border border-slate-200/80 shadow-sm hover:border-indigo-300 hover:shadow-md transition-all flex flex-col justify-between">
                    <div>
                        <div class="flex justify-between items-start">
                            <div>
                                <span class="px-2.5 py-0.5 bg-slate-100 text-slate-700 font-bold text-[11px] uppercase tracking-wider rounded-md">
                                    Rank #${idx + 2}
                                </span>
                                <h4 class="text-xl font-black text-slate-900 mt-2">${rec.career_title}</h4>
                            </div>
                            <span class="text-2xl font-black text-indigo-600">${rec.match_score}%</span>
                        </div>

                        <div class="mt-4 pt-3 border-t border-slate-100">
                            <p class="text-[11px] font-bold text-indigo-600 uppercase tracking-wider">Explainability Path:</p>
                            <p class="text-xs text-slate-600 mt-1 leading-relaxed">${rec.reasoning_path}</p>
                        </div>

                        ${matchedHtml}
                        ${missingHtml}
                    </div>

                    <div class="mt-6 pt-4 border-t border-slate-100">
                        <a href="/jobs?q=${encodeURIComponent(rec.career_title)}" 
                           class="w-full py-2.5 px-4 bg-slate-100 hover:bg-indigo-50 hover:text-indigo-600 text-slate-700 font-bold text-xs rounded-xl transition text-center block">
                            Apply & View Indian Jobs →
                        </a>
                    </div>
                </div>
            `;
        });

        recsContainer.innerHTML = `
            <!-- Hero Card: Rank 1 -->
            <div class="bg-gradient-to-br from-indigo-900 via-slate-900 to-slate-900 text-white p-7 sm:p-9 rounded-3xl shadow-xl border border-indigo-800/40 relative overflow-hidden">
                <div class="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>
                
                <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 relative z-10">
                    <div>
                        <span class="px-3 py-1 bg-amber-400 text-slate-950 font-black text-xs uppercase tracking-wider rounded-lg shadow-sm">
                            ★ Top Match (Rank #1)
                        </span>
                        <h3 class="text-2xl sm:text-3xl font-black mt-3 tracking-tight">${hero.career_title}</h3>
                    </div>
                    <div class="text-left sm:text-right">
                        <span class="text-4xl sm:text-5xl font-black text-amber-400 tracking-tight">${hero.match_score}%</span>
                        <p class="text-xs text-slate-400 font-bold uppercase tracking-wider">KGIMCS Affinity Score</p>
                    </div>
                </div>

                <div class="mt-6 pt-5 border-t border-slate-700/60 relative z-10">
                    <p class="text-xs font-bold text-indigo-300 uppercase tracking-wider">Why Recommended (Traceable Graph Path):</p>
                    <p class="text-sm text-slate-300 mt-1 leading-relaxed">${hero.reasoning_path}</p>
                </div>

                <div class="mt-6 pt-5 border-t border-slate-700/60 flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative z-10">
                    <div class="space-y-1 flex-1 w-full">
                        ${heroMatchedHtml}
                        ${heroMissingHtml}
                    </div>

                    <a href="/jobs?q=${encodeURIComponent(hero.career_title)}" 
                       class="w-full md:w-auto px-6 py-3 bg-amber-400 hover:bg-amber-300 text-slate-950 font-extrabold text-sm rounded-xl shadow-lg transition-all text-center flex items-center justify-center gap-2 flex-shrink-0">
                        Explore Jobs for ${hero.career_title} →
                    </a>
                </div>
            </div>

            <!-- Grid for Ranks 2, 3, 4, 5 -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                ${gridHtml}
            </div>
        `;
    }
});