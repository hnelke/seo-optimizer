document.addEventListener('DOMContentLoaded', () => {
    // === DOM ELEMENTS ===
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const htmlElement = document.documentElement;
    
    // View Sections
    const navAuditBtn = document.getElementById('navAuditBtn');
    const navHistoryBtn = document.getElementById('navHistoryBtn');
    const navGlossaryBtn = document.getElementById('navGlossaryBtn');
    const historyCount = document.getElementById('historyCount');
    const auditInputArea = document.getElementById('auditInputArea');
    const dashboardSection = document.getElementById('dashboardSection');
    const historySection = document.getElementById('historySection');
    const comparisonSection = document.getElementById('comparisonSection');
    
    // Forms & Inputs
    const analyzeForm = document.getElementById('analyzeForm');
    const urlInput = document.getElementById('urlInput');
    const btnSpinner = document.getElementById('btnSpinner');
    const errorBanner = document.getElementById('errorBanner');
    const errorMsg = document.getElementById('errorMsg');
    
    // Loader
    const loadingSection = document.getElementById('loadingSection');
    const loaderStatusText = document.getElementById('loaderStatusText');
    const step1 = document.getElementById('step1');
    const step2 = document.getElementById('step2');
    const step3 = document.getElementById('step3');
    const step4 = document.getElementById('step4');
    const step5 = document.getElementById('step5');
    
    // Gauges & Overview
    const overallScoreFill = document.getElementById('overallScoreFill');
    const overallScoreVal = document.getElementById('overallScoreVal');
    const overallFeedback = document.getElementById('overallFeedback');
    
    const seoScoreVal = document.getElementById('seoScoreVal');
    const seoScoreBar = document.getElementById('seoScoreBar');
    const aeoScoreVal = document.getElementById('aeoScoreVal');
    const aeoScoreBar = document.getElementById('aeoScoreBar');
    const schemaScoreVal = document.getElementById('schemaScoreVal');
    const schemaScoreBar = document.getElementById('schemaScoreBar');
    const eeatScoreVal = document.getElementById('eeatScoreVal');
    const eeatScoreBar = document.getElementById('eeatScoreBar');
    const textScoreVal = document.getElementById('textScoreVal');
    const textScoreBar = document.getElementById('textScoreBar');
    
    // Summary lists
    const criticalList = document.getElementById('criticalList');
    const optimizationList = document.getElementById('optimizationList');
    const successList = document.getElementById('successList');
    
    // Overview stats
    const statH1Count = document.getElementById('statH1Count');
    const statQuestions = document.getElementById('statQuestions');
    const statImages = document.getElementById('statImages');
    const statSchemaCount = document.getElementById('statSchemaCount');
    const statAvgSentence = document.getElementById('statAvgSentence');
    const statExternalLinks = document.getElementById('statExternalLinks');
    const metaAuditedUrl = document.getElementById('metaAuditedUrl');
    const reAuditDashboardBtn = document.getElementById('reAuditDashboardBtn');
    
    // Tab detailed lists
    const qaPairsList = document.getElementById('qaPairsList');
    const schemaListContainer = document.getElementById('schemaListContainer');
    const outlineTreeContainer = document.getElementById('outlineTreeContainer');
    const eeatTrustTags = document.getElementById('eeatTrustTags');
    const eeatCitationsList = document.getElementById('eeatCitationsList');
    
    // Generator
    const faqQuestionsContainer = document.getElementById('faqQuestionsContainer');
    const addQuestionBtn = document.getElementById('addQuestionBtn');
    const generateSchemaBtn = document.getElementById('generateSchemaBtn');
    const copySchemaBtn = document.getElementById('copySchemaBtn');
    const schemaOutputText = document.getElementById('schemaOutputText');
    
    // History Panel Elements
    const historyList = document.getElementById('historyList');
    const compareActionsBar = document.getElementById('compareActionsBar');
    const compareInfoText = document.getElementById('compareInfoText');
    const triggerCompareBtn = document.getElementById('triggerCompareBtn');
    const historySearchInput = document.getElementById('historySearchInput');
    const historyScoreOp = document.getElementById('historyScoreOp');
    const historyScoreVal = document.getElementById('historyScoreVal');
    const historySortSelect = document.getElementById('historySortSelect');
    
    // Comparison Panel Elements
    const backToHistoryBtn = document.getElementById('backToHistoryBtn');
    const comparisonMeta = document.getElementById('comparisonMeta');
    const compDateOld = document.getElementById('compDateOld');
    const compScoreOld = document.getElementById('compScoreOld');
    const compDateNew = document.getElementById('compDateNew');
    const compScoreNew = document.getElementById('compScoreNew');
    const compScoreDelta = document.getElementById('compScoreDelta');
    
    const compSeoOld = document.getElementById('compSeoOld');
    const compSeoNew = document.getElementById('compSeoNew');
    const compSeoDelta = document.getElementById('compSeoDelta');
    const compAeoOld = document.getElementById('compAeoOld');
    const compAeoNew = document.getElementById('compAeoNew');
    const compAeoDelta = document.getElementById('compAeoDelta');
    const compSchemaOld = document.getElementById('compSchemaOld');
    const compSchemaNew = document.getElementById('compSchemaNew');
    const compSchemaDelta = document.getElementById('compSchemaDelta');
    const compEeatOld = document.getElementById('compEeatOld');
    const compEeatNew = document.getElementById('compEeatNew');
    const compEeatDelta = document.getElementById('compEeatDelta');
    
    const compImprovedList = document.getElementById('compImprovedList');
    const compWorsenedList = document.getElementById('compWorsenedList');

    // === STATE VARIABLES ===
    let selectedRuns = []; // holds { domain, timestamp } objects selected for comparison
    let historyDomainsCache = {}; // holds the raw fetched domains history data
    let currentPage = 1;
    let pageSize = 10;
    let openDomain = null; // keeps track of the currently expanded domain accordion
    let runsSortCol = 'timestamp'; // 'timestamp' or 'overall_score'
    let runsSortOrder = 'desc'; // 'asc' or 'desc'

    // === THEME MANAGER ===
    const savedTheme = localStorage.getItem('theme') || 'dark';
    if (savedTheme === 'light') {
        htmlElement.classList.add('light-mode');
    }

    themeToggleBtn.addEventListener('click', () => {
        if (htmlElement.classList.contains('light-mode')) {
            htmlElement.classList.remove('light-mode');
            localStorage.setItem('theme', 'dark');
        } else {
            htmlElement.classList.add('light-mode');
            localStorage.setItem('theme', 'light');
        }
    });

    // === ADVANCED SETTINGS PANEL TOGGLE ===
    const advancedToggle = document.getElementById('advancedToggle');
    const advancedPanel = document.getElementById('advancedPanel');
    const geminiApiKeyInput = document.getElementById('geminiApiKeyInput');
    
    if (advancedToggle && advancedPanel) {
        // Load key from localStorage
        const storedKey = localStorage.getItem('gemini_api_key') || '';
        if (geminiApiKeyInput) {
            geminiApiKeyInput.value = storedKey;
        }
        
        advancedToggle.addEventListener('click', () => {
            const isOpen = advancedPanel.style.display === 'block';
            advancedPanel.style.display = isOpen ? 'none' : 'block';
            const arrow = advancedToggle.querySelector('.arrow-icon');
            if (arrow) {
                arrow.style.transform = isOpen ? 'rotate(0deg)' : 'rotate(90deg)';
            }
        });
    }

    // === VIEW CONTROLLER (TOP NAVIGATION) ===
    navAuditBtn.addEventListener('click', () => {
        if (window.location.hash === '#audit') {
            handleHashRoute();
        } else {
            window.location.hash = 'audit';
        }
    });

    navHistoryBtn.addEventListener('click', () => {
        if (window.location.hash === '#history') {
            handleHashRoute();
        } else {
            window.location.hash = 'history';
        }
    });

    // Event listeners for history filtering and sorting
    if (historySearchInput) {
        historySearchInput.addEventListener('input', () => { currentPage = 1; filterAndRenderHistory(); });
    }
    if (historyScoreOp) {
        historyScoreOp.addEventListener('change', () => { currentPage = 1; filterAndRenderHistory(); });
    }
    if (historyScoreVal) {
        historyScoreVal.addEventListener('input', () => { currentPage = 1; filterAndRenderHistory(); });
    }
    if (historySortSelect) {
        historySortSelect.addEventListener('change', () => { currentPage = 1; filterAndRenderHistory(); });
    }

    // Pagination Controls Listeners
    const pageSizeBtns = document.querySelectorAll('.page-size-btn');
    pageSizeBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            pageSizeBtns.forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            pageSize = parseInt(e.target.getAttribute('data-size')) || 10;
            currentPage = 1;
            filterAndRenderHistory();
        });
    });

    const prevPageBtn = document.getElementById('prevPageBtn');
    const nextPageBtn = document.getElementById('nextPageBtn');

    if (prevPageBtn) {
        prevPageBtn.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                filterAndRenderHistory();
            }
        });
    }
    if (nextPageBtn) {
        nextPageBtn.addEventListener('click', () => {
            currentPage++;
            filterAndRenderHistory();
        });
    }

    function switchView(view) {
        // Reset navigation buttons
        navAuditBtn.classList.remove('active');
        navHistoryBtn.classList.remove('active');
        if (navGlossaryBtn) {
            navGlossaryBtn.classList.remove('active');
        }
        
        // Hide all views
        auditInputArea.style.display = 'none';
        dashboardSection.style.display = 'none';
        historySection.style.display = 'none';
        comparisonSection.style.display = 'none';
        
        if (view === 'audit') {
            navAuditBtn.classList.add('active');
            auditInputArea.style.display = 'block';
            // If we have an active analysis on the dashboard, show it
            if (overallScoreVal.textContent !== '0') {
                dashboardSection.style.display = 'block';
            }
        } else if (view === 'history') {
            navHistoryBtn.classList.add('active');
            historySection.style.display = 'block';
        } else if (view === 'comparison') {
            comparisonSection.style.display = 'block';
        }
    }

    // === HASH ROUTING FOR DEEP LINKING ===
    function handleHashRoute() {
        const hash = window.location.hash;
        if (hash === '#history') {
            switchView('history');
            loadHistory();
        } else {
            switchView('audit');
        }
    }

    // Call on load and register hashchange event listener
    handleHashRoute();
    window.addEventListener('hashchange', handleHashRoute);

    // Load initial history count on startup
    updateHistoryCount();

    // === TABS CONTROL ===
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            tabButtons.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });

    // === API CRAWL AND ANALYSIS ===
    if (urlInput) {
        urlInput.addEventListener('input', () => {
            urlInput.value = urlInput.value.toLowerCase();
        });
    }

    analyzeForm.addEventListener('submit', (e) => {
        e.preventDefault();
        triggerAudit(urlInput.value.trim().toLowerCase());
    });

    async function triggerAudit(url) {
        if (!url) return;
        url = url.toLowerCase();

        // Reset UI States
        errorBanner.style.display = 'none';
        dashboardSection.style.display = 'none';
        loadingSection.style.display = 'block';
        btnSpinner.style.display = 'inline-block';
        urlInput.value = url;
        
        resetProgressSteps();
        
        // Retrieve and store api key
        const apiKey = geminiApiKeyInput ? geminiApiKeyInput.value.trim() : '';
        if (geminiApiKeyInput) {
            localStorage.setItem('gemini_api_key', apiKey);
        }
        
        try {
            updateLoaderStatus('Rufe HTML ab und durchsuche Inhalte...', 1);
            
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    url: url,
                    gemini_api_key: apiKey || null
                })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Fehler bei der Seitenanalyse.');
            }

            const data = await response.json();
            
            await animateProgressSteps();

            // Populate Report
            displayReport(data);

            // Hide loader and show dashboard
            loadingSection.style.display = 'none';
            dashboardSection.style.display = 'block';
            
            // Update counts
            updateHistoryCount();

            // Scroll to overall score (Gesamtscore) with offset for sticky header
            setTimeout(() => {
                const mainGaugeCard = document.querySelector('.main-gauge-card');
                if (mainGaugeCard) {
                    const stickyNav = document.querySelector('.sticky-nav-wrapper');
                    const offset = stickyNav ? stickyNav.offsetHeight + 16 : 100;
                    const bodyRect = document.body.getBoundingClientRect().top;
                    const elementRect = mainGaugeCard.getBoundingClientRect().top;
                    const elementPosition = elementRect - bodyRect;
                    const offsetPosition = elementPosition - offset;
                    
                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                }
            }, 100);

        } catch (error) {
            loadingSection.style.display = 'none';
            errorBanner.style.display = 'flex';
            errorMsg.textContent = error.message;
        } finally {
            btnSpinner.style.display = 'none';
        }
    }

    function resetProgressSteps() {
        const steps = [step1, step2, step3, step4, step5];
        steps.forEach(s => s.classList.remove('active', 'done'));
        step1.classList.add('active');
    }

    function updateLoaderStatus(text, stepNumber) {
        loaderStatusText.textContent = text;
        const steps = [step1, step2, step3, step4, step5];
        for (let i = 0; i < steps.length; i++) {
            if (i < stepNumber - 1) {
                steps[i].classList.remove('active');
                steps[i].classList.add('done');
            } else if (i === stepNumber - 1) {
                steps[i].classList.add('active');
            }
        }
    }

    async function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async function animateProgressSteps() {
        updateLoaderStatus('Werte SEO & AEO-Metriken aus...', 2);
        await sleep(400);
        updateLoaderStatus('Prüfe JSON-LD Schema Markups...', 3);
        await sleep(400);
        updateLoaderStatus('Bewerte E-E-A-T Glaubwürdigkeitssignale...', 4);
        await sleep(400);
        updateLoaderStatus('Führe Text-Qualitätsanalyse durch...', 5);
        await sleep(400);
        step5.classList.remove('active');
        step5.classList.add('done');
    }

    // Re-Audit Dashboard Button
    reAuditDashboardBtn.addEventListener('click', () => {
        const url = metaAuditedUrl.textContent;
        switchView('audit');
        triggerAudit(url);
    });

    // === DISPLAY REPORT DETAILED DATA ===
    function displayReport(report) {
        // Overall Score Gauge
        const score = report.overall_score;
        overallScoreVal.textContent = score;
        
        const circumference = 314.16;
        const offset = circumference - (score / 100) * circumference;
        overallScoreFill.style.strokeDashoffset = offset;
        
        if (score >= 80) {
            overallScoreFill.style.stroke = 'var(--accent-emerald)';
            overallFeedback.textContent = "Hervorragend! Deine Seite ist exzellent auf Suchmaschinen und KI-Overviews vorbereitet.";
        } else if (score >= 50) {
            overallScoreFill.style.stroke = 'var(--accent-amber)';
            overallFeedback.textContent = "Gute Basis, aber es gibt noch signifikante Potenziale zur KI-Suchoptimierung.";
        } else {
            overallScoreFill.style.stroke = 'var(--accent-rose)';
            overallFeedback.textContent = "Kritisch: Die Seite weist erhebliche Defizite auf und wird von KIs kaum berücksichtigt.";
        }

        // Subscore Bars
        animateBar(seoScoreBar, seoScoreVal, report.scores.seo);
        animateBar(aeoScoreBar, aeoScoreVal, report.scores.aeo);
        animateBar(schemaScoreBar, schemaScoreVal, report.scores.schema);
        animateBar(eeatScoreBar, eeatScoreVal, report.scores.eeat);
        
        const textScore = report.scores.hasOwnProperty('text') ? report.scores.text : 0;
        animateBar(textScoreBar, textScoreVal, textScore);

        // Handlungsbedarf Lists
        populateList(criticalList, report.summary.critical, 'danger');
        populateList(optimizationList, report.summary.optimization, 'warning');
        populateList(successList, report.summary.success, 'success');

        // Tab 1: Stats Overview
        statH1Count.textContent = report.reports.seo.data.h1_count;
        statQuestions.textContent = report.reports.aeo.data.question_headings;
        statImages.textContent = report.reports.seo.data.image_count;
        statSchemaCount.textContent = report.reports.schema.data.schema_count;
        statAvgSentence.textContent = report.reports.aeo.data.avg_sentence_len;
        statExternalLinks.textContent = report.reports.eeat.data.authority_citations_count;
        metaAuditedUrl.textContent = report.url;

        // Tab 2: AEO Q&A pairs
        qaPairsList.innerHTML = '';
        const qaPairs = report.reports.aeo.qa_pairs;
        if (qaPairs && qaPairs.length > 0) {
            qaPairs.forEach(pair => {
                const qaCard = document.createElement('div');
                qaCard.className = `qa-card qa-${pair.status}`;
                qaCard.innerHTML = `
                    <div class="qa-header">
                        <span class="qa-heading"><span class="outline-tag">${pair.heading_type}</span> ${pair.heading}</span>
                        <div class="qa-badge-group">
                            <span class="badge ${getBadgeClass(pair.status)}">${pair.rating}</span>
                            <span class="qa-tag">${pair.word_count} Wörter</span>
                        </div>
                    </div>
                    <div class="qa-answer-box">${pair.answer_preview}</div>
                    <div class="qa-feedback">${pair.feedback}</div>
                `;
                qaPairsList.appendChild(qaCard);
            });
        } else {
            qaPairsList.innerHTML = `
                <div class="qa-card qa-needs_work">
                    <p style="margin-bottom:0">Keine fragebasierten Abschnitte auf dieser Seite gefunden. Du solltest Überschriften formulieren, die direkt Nutzerfragen beantworten.</p>
                </div>
            `;
        }

        // Tab 3: Schema Explorer JSONs
        schemaListContainer.innerHTML = '';
        const foundSchemas = report.reports.schema.found_schemas;
        if (foundSchemas && foundSchemas.length > 0) {
            foundSchemas.forEach((schema, idx) => {
                const schemaBox = document.createElement('div');
                schemaBox.className = 'schema-object';
                const type = schema['@type'] || 'Unbekannt';
                schemaBox.innerHTML = `
                    <h4>#${idx + 1} Typ: ${type}</h4>
                    <pre><code>${escapeHtml(JSON.stringify(schema, null, 2))}</code></pre>
                `;
                schemaListContainer.appendChild(schemaBox);
            });
        } else {
            schemaListContainer.innerHTML = `
                <div class="qa-card qa-danger">
                    <p style="margin-bottom:0">Keine Schema-Markups im JSON-LD-Format auf der Seite entdeckt. Verwende den Generator-Tab zum Erstellen.</p>
                </div>
            `;
        }

        // Tab 4: Outline Hierarchical Tree
        outlineTreeContainer.innerHTML = '';
        const headingOutline = report.reports.aeo.heading_outline;
        if (headingOutline && headingOutline.length > 0) {
            headingOutline.forEach(h => {
                const item = document.createElement('div');
                item.className = `outline-tree-item outline-level-${h.level}`;
                item.innerHTML = `
                    <span><span class="outline-tag">${h.tag}</span>${h.text}</span>
                    ${h.is_question ? '<span class="outline-question-badge">Nutzerfrage</span>' : ''}
                `;
                outlineTreeContainer.appendChild(item);
            });
        } else {
            outlineTreeContainer.innerHTML = '<p>Keine Überschriften auf dieser Seite vorhanden.</p>';
        }

        // Tab 5: E-E-A-T details
        eeatTrustTags.innerHTML = '';
        const trustPages = report.reports.eeat.trust_links;
        const allTrustTypes = ['impressum', 'datenschutz', 'kontakt', 'ueber_uns'];
        const detectedTypes = trustPages.map(p => p.type);
        
        allTrustTypes.forEach(type => {
            const tag = document.createElement('span');
            const hasIt = detectedTypes.includes(type);
            const name = type.replace('_', ' ').toUpperCase();
            
            if (hasIt) {
                tag.className = 'trust-tag-item';
                tag.innerHTML = `✓ ${name}`;
            } else {
                tag.className = 'trust-tag-item missing';
                tag.innerHTML = `✗ ${name} (Fehlt)`;
            }
            eeatTrustTags.appendChild(tag);
        });

        eeatCitationsList.innerHTML = '';
        const detailsEeat = report.reports.eeat.details;
        const citationDetail = detailsEeat.find(d => d.id === 'citations_found');
        
        if (citationDetail && report.reports.eeat.data.authority_citations_count > 0) {
            const citationsInfo = citationDetail.info.replace("Referenz-URLs: ", "").split(", ");
            citationsInfo.forEach(link => {
                const li = document.createElement('li');
                li.innerHTML = `<a href="${link}" target="_blank" rel="noopener noreferrer">${link}</a>`;
                eeatCitationsList.appendChild(li);
            });
        } else {
            eeatCitationsList.innerHTML = '<li>Keine autoritativen Links gefunden. Die Verlinkung vertrauenswürdiger dritter Quellen stärkt die E-E-A-T Bewertung.</li>';
        }

        // Tab Text-Bewertung Rendering
        const textEvalTab = document.getElementById('textEvalTab');
        if (textEvalTab) {
            const textReport = report.reports ? report.reports.text : null;
            if (textReport) {
                const banner = document.getElementById('textEvalAiBanner');
                
                if (banner) {
                    if (textReport.is_ai_analyzed) {
                        banner.style.backgroundColor = 'rgba(99, 102, 241, 0.15)';
                        banner.style.border = '1px solid rgba(99, 102, 241, 0.25)';
                        banner.style.color = '#a5b4fc';
                        banner.innerHTML = `
                            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" style="flex-shrink:0;">
                                <polygon points="12 2 2 22 22 22 12 2"></polygon>
                                <line x1="12" y1="9" x2="12" y2="13"></line>
                                <line x1="12" y1="17" x2="12.01" y2="17"></line>
                            </svg>
                            <span>Analysemodus: <strong>KI-basiert (Gemini 2.5 Flash)</strong>. Hochpräzise semantische Textauswertung.</span>
                        `;
                    } else {
                        banner.style.backgroundColor = 'rgba(245, 158, 11, 0.15)';
                        banner.style.border = '1px solid rgba(245, 158, 11, 0.25)';
                        banner.style.color = '#fde047';
                        banner.innerHTML = `
                            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" style="flex-shrink:0;">
                                <circle cx="12" cy="12" r="10"></circle>
                                <line x1="12" y1="8" x2="12" y2="12"></line>
                                <line x1="12" y1="16" x2="12.01" y2="16"></line>
                            </svg>
                            <span>Analysemodus: <strong>Lokale Heuristik (Fallback)</strong>. Um die präzisere KI-Auswertung freizuschalten, fügen Sie oben einen Gemini API-Key hinzu.</span>
                        `;
                    }
                }
                
                const renderStars = (elId, score) => {
                    const el = document.getElementById(elId);
                    if (el) {
                        el.innerHTML = '';
                        for (let i = 1; i <= 5; i++) {
                            const star = document.createElement('span');
                            star.textContent = i <= score ? '★' : '☆';
                            el.appendChild(star);
                        }
                    }
                };
                
                const renderRecs = (elId, recs) => {
                    const el = document.getElementById(elId);
                    if (el) {
                        el.innerHTML = '';
                        if (recs && recs.length > 0) {
                            recs.forEach(rec => {
                                const li = document.createElement('li');
                                li.style.fontSize = '0.82rem';
                                li.style.color = 'var(--text-secondary)';
                                li.style.marginBottom = '0.35rem';
                                li.style.paddingLeft = '1rem';
                                li.style.position = 'relative';
                                li.innerHTML = `<span style="position:absolute; left:0; color:var(--accent-violet)">•</span> ${rec}`;
                                el.appendChild(li);
                            });
                        } else {
                            el.innerHTML = '<li>Keine Empfehlungen.</li>';
                        }
                    }
                };
                
                const data = textReport.data;
                if (data) {
                    // Klarheit
                    renderStars('starsKlarheit', data.klarheit ? data.klarheit.score : 0);
                    document.getElementById('descKlarheit').textContent = data.klarheit ? data.klarheit.explanation : '';
                    renderRecs('recsKlarheit', data.klarheit ? data.klarheit.recommendations : []);
                    
                    // Originalität
                    renderStars('starsOriginalitaet', data.originalitaet ? data.originalitaet.score : 0);
                    document.getElementById('descOriginalitaet').textContent = data.originalitaet ? data.originalitaet.explanation : '';
                    renderRecs('recsOriginalitaet', data.originalitaet ? data.originalitaet.recommendations : []);
                    
                    // Emotion
                    renderStars('starsEmotion', data.emotion ? data.emotion.score : 0);
                    document.getElementById('descEmotion').textContent = data.emotion ? data.emotion.explanation : '';
                    renderRecs('recsEmotion', data.emotion ? data.emotion.recommendations : []);
                    
                    // Konkretheit
                    renderStars('starsKonkretheit', data.konkretheit ? data.konkretheit.score : 0);
                    document.getElementById('descKonkretheit').textContent = data.konkretheit ? data.konkretheit.explanation : '';
                    renderRecs('recsKonkretheit', data.konkretheit ? data.konkretheit.recommendations : []);
                }
            } else {
                // Handle old reports without text audit data
                const banner = document.getElementById('textEvalAiBanner');
                if (banner) {
                    banner.style.backgroundColor = 'rgba(239, 68, 68, 0.15)';
                    banner.style.border = '1px solid rgba(239, 68, 68, 0.25)';
                    banner.style.color = '#f87171';
                    banner.innerHTML = `
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" style="flex-shrink:0;">
                            <circle cx="12" cy="12" r="10"></circle>
                            <line x1="12" y1="8" x2="12" y2="12"></line>
                            <line x1="12" y1="16" x2="12.01" y2="16"></line>
                        </svg>
                        <span>Dieser Bericht wurde vor der Einführung des Text-Audits erstellt. Starten Sie eine neue Analyse, um Textbewertungen zu erhalten.</span>
                    `;
                }
                document.getElementById('descKlarheit').textContent = 'Keine Daten in diesem alten Bericht vorhanden.';
                document.getElementById('descOriginalitaet').textContent = 'Keine Daten in diesem alten Bericht vorhanden.';
                document.getElementById('descEmotion').textContent = 'Keine Daten in diesem alten Bericht vorhanden.';
                document.getElementById('descKonkretheit').textContent = 'Keine Daten in diesem alten Bericht vorhanden.';
                
                document.getElementById('starsKlarheit').innerHTML = '';
                document.getElementById('starsOriginalitaet').innerHTML = '';
                document.getElementById('starsEmotion').innerHTML = '';
                document.getElementById('starsKonkretheit').innerHTML = '';
                
                document.getElementById('recsKlarheit').innerHTML = '';
                document.getElementById('recsOriginalitaet').innerHTML = '';
                document.getElementById('recsEmotion').innerHTML = '';
                document.getElementById('recsKonkretheit').innerHTML = '';
            }
        }
    }

    function animateBar(barElement, valElement, targetScore) {
        barElement.style.width = '0%';
        valElement.textContent = `0/100`;
        setTimeout(() => {
            barElement.style.width = `${targetScore}%`;
            valElement.textContent = `${targetScore}/100`;
            
            if (targetScore >= 80) {
                barElement.style.background = 'linear-gradient(90deg, var(--accent-emerald), #34d399)';
            } else if (targetScore >= 50) {
                barElement.style.background = 'linear-gradient(90deg, var(--accent-amber), #fbbf24)';
            } else {
                barElement.style.background = 'linear-gradient(90deg, var(--accent-rose), #f87171)';
            }
        }, 100);
    }

    function populateList(ulElement, items, type) {
        ulElement.innerHTML = '';
        if (items && items.length > 0) {
            items.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item;
                ulElement.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = type === 'danger' ? 'Keine kritischen Probleme.' : type === 'warning' ? 'Keine ausstehenden Optimierungen.' : 'Keine Audits gelistet.';
            ulElement.appendChild(li);
        }
    }

    function getBadgeClass(status) {
        if (status === 'optimized') return 'badge-success';
        if (status === 'needs_work') return 'badge-warning';
        return 'badge-danger';
    }

    function escapeHtml(text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // === HISTORIEN & DATENBANK LOGIK ===

    async function updateHistoryCount() {
        try {
            const response = await fetch('/api/history');
            if (response.ok) {
                const data = await response.json();
                let count = 0;
                Object.keys(data.domains).forEach(dom => {
                    count += data.domains[dom].length;
                });
                historyCount.textContent = count;
            }
        } catch (e) {
            console.error('Fehler beim Abrufen der Historien-Anzahl', e);
        }
    }

    async function loadHistory() {
        historyList.innerHTML = '<p class="empty-history-text">Lade Historie...</p>';
        selectedRuns = [];
        openDomain = null;
        currentPage = 1; // Reset to page 1 on load
        updateCompareActionBar();
        
        try {
            const response = await fetch('/api/history');
            if (!response.ok) throw new Error('Fehler beim Laden der Verlaufshistorie.');
            
            const data = await response.json();
            historyDomainsCache = data.domains || {};
            
            filterAndRenderHistory();
        } catch (e) {
            historyList.innerHTML = `<p class="empty-history-text" style="color:var(--accent-rose)">${e.message}</p>`;
        }
    }

    function filterAndRenderHistory() {
        if (!historyList) return;
        
        const query = (historySearchInput ? historySearchInput.value : '').toLowerCase().trim();
        const scoreOp = historyScoreOp ? historyScoreOp.value : 'all';
        const scoreLimit = historyScoreVal ? parseInt(historyScoreVal.value, 10) : NaN;
        const sortBy = historySortSelect ? historySortSelect.value : 'score_desc';
        
        let filteredDomains = Object.keys(historyDomainsCache).filter(dom => {
            // 1. Search Query
            if (query && !dom.toLowerCase().includes(query)) {
                return false;
            }
            
            // 2. Score Filter
            const runs = historyDomainsCache[dom];
            if (!runs || runs.length === 0) return false;
            const lastRun = runs[runs.length - 1];
            const lastScore = lastRun.overall_score;
            
            if (scoreOp !== 'all' && !isNaN(scoreLimit)) {
                if (scoreOp === 'gte' && !(lastScore >= scoreLimit)) return false;
                if (scoreOp === 'gt' && !(lastScore > scoreLimit)) return false;
                if (scoreOp === 'lte' && !(lastScore <= scoreLimit)) return false;
                if (scoreOp === 'lt' && !(lastScore < scoreLimit)) return false;
            }
            
            return true;
        });
        
        // Sorting
        filteredDomains.sort((a, b) => {
            const runsA = historyDomainsCache[a];
            const runsB = historyDomainsCache[b];
            const lastA = runsA[runsA.length - 1];
            const lastB = runsB[runsB.length - 1];
            
            if (sortBy === 'newest') {
                return new Date(lastB.timestamp) - new Date(lastA.timestamp);
            } else if (sortBy === 'score_desc') {
                return lastB.overall_score - lastA.overall_score;
            } else if (sortBy === 'score_asc') {
                return lastA.overall_score - lastB.overall_score;
            } else if (sortBy === 'alphabetical') {
                return a.localeCompare(b);
            }
            return 0;
        });
        
        historyList.innerHTML = '';
        
        const paginationContainer = document.getElementById('historyPagination');
        if (filteredDomains.length === 0) {
            historyList.innerHTML = '<p class="empty-history-text">Keine passenden historischen Audits gefunden.</p>';
            if (paginationContainer) paginationContainer.style.display = 'none';
            return;
        } else {
            if (paginationContainer) paginationContainer.style.display = 'flex';
        }

        // Pagination calculation
        const totalFiltered = filteredDomains.length;
        const totalPages = Math.ceil(totalFiltered / pageSize) || 1;
        if (currentPage > totalPages) currentPage = totalPages;
        if (currentPage < 1) currentPage = 1;

        const startIndex = (currentPage - 1) * pageSize;
        const endIndex = Math.min(startIndex + pageSize, totalFiltered);
        const paginatedDomains = filteredDomains.slice(startIndex, endIndex);

        renderPaginationNav(totalFiltered, totalPages);
        
        paginatedDomains.forEach(dom => {
            const group = document.createElement('div');
            group.className = 'history-domain-group';
            
            const runs = historyDomainsCache[dom];
            const lastRun = runs[runs.length - 1];
            const formattedDate = formatDate(lastRun.timestamp);
            
            group.innerHTML = `
                <div class="domain-header">
                    <div class="domain-title-side">
                        <span class="domain-icon" style="display: inline-flex; align-items: center;">
                            <svg class="icon-svg domain-folder-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                            </svg>
                        </span>
                        <span class="domain-name">${dom}</span>
                    </div>
                    <div class="domain-meta-side">
                        <span class="badge ${getScoreBadgeClass(lastRun.overall_score)}">Letzter Score: ${lastRun.overall_score}</span>
                        <span style="font-size:0.8rem; color:var(--text-secondary)">${runs.length} Scan(s)</span>
                        <button class="btn-delete-domain" title="Domain komplett löschen">
                            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <polyline points="3 6 5 6 21 6"></polyline>
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                <line x1="10" y1="11" x2="10" y2="17"></line>
                                <line x1="14" y1="11" x2="14" y2="17"></line>
                            </svg>
                        </button>
                        <span class="accordion-arrow">
                            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <polyline points="9 18 15 12 9 6"></polyline>
                            </svg>
                        </span>
                    </div>
                </div>
                <div class="domain-runs-container">
                    <div class="run-row header-row">
                        <div></div>
                        <div class="sortable-run-header" data-sort-col="timestamp" style="cursor: pointer; user-select: none; display: inline-flex; align-items: center; gap: 0.25rem;">
                            Zeitpunkt ${runsSortCol === 'timestamp' ? (runsSortOrder === 'asc' ? '▲' : '▼') : '↕'}
                        </div>
                        <div class="sortable-run-header" data-sort-col="overall_score" style="cursor: pointer; user-select: none; display: inline-flex; align-items: center; gap: 0.25rem;">
                            Score ${runsSortCol === 'overall_score' ? (runsSortOrder === 'asc' ? '▲' : '▼') : '↕'}
                        </div>
                        <div style="text-align:right">Aktionen</div>
                    </div>
                    <!-- Runs rows injected below -->
                </div>
            `;
            
            const runsContainer = group.querySelector('.domain-runs-container');
            
            // Restore open state
            if (dom === openDomain) {
                group.classList.add('open');
            }
            
            // Add accordion toggle event
            group.querySelector('.domain-header').addEventListener('click', (e) => {
                // Prevent toggle if clicking on delete domain button or any child of it
                if (e.target.closest('.btn-delete-domain')) return;
                
                const isOpen = group.classList.contains('open');
                // Close all others
                document.querySelectorAll('.history-domain-group').forEach(g => g.classList.remove('open'));
                if (!isOpen) {
                    group.classList.add('open');
                    openDomain = dom;
                } else {
                    group.classList.remove('open');
                    openDomain = null;
                }
            });
            
            // Wire delete domain button
            const deleteDomBtn = group.querySelector('.btn-delete-domain');
            deleteDomBtn.addEventListener('click', async (e) => {
                e.stopPropagation(); // Stop toggle accordion event
                const message = `Möchtest du die Domain "${dom}" und alle zugehörigen ${runs.length} Scan-Berichte wirklich komplett löschen?`;
                if (await showCustomConfirm(message, "Domain löschen?")) {
                    await deleteDomain(dom);
                }
            });

            // Wire sort headers
            const timestampHeader = group.querySelector('[data-sort-col="timestamp"]');
            const scoreHeader = group.querySelector('[data-sort-col="overall_score"]');
            
            const handleSortClick = (col) => {
                if (runsSortCol === col) {
                    runsSortOrder = runsSortOrder === 'asc' ? 'desc' : 'asc';
                } else {
                    runsSortCol = col;
                    runsSortOrder = 'desc'; // default to newest / highest score first
                }
                filterAndRenderHistory();
            };
            
            if (timestampHeader) {
                timestampHeader.addEventListener('click', (e) => {
                    e.stopPropagation();
                    handleSortClick('timestamp');
                });
            }
            if (scoreHeader) {
                scoreHeader.addEventListener('click', (e) => {
                    e.stopPropagation();
                    handleSortClick('overall_score');
                });
            }
            
            // Populate runs (sorted)
            const sortedRuns = [...runs];
            sortedRuns.sort((a, b) => {
                let valA, valB;
                if (runsSortCol === 'timestamp') {
                    valA = new Date(a.timestamp);
                    valB = new Date(b.timestamp);
                } else {
                    valA = a.overall_score;
                    valB = b.overall_score;
                }
                
                if (runsSortOrder === 'asc') {
                    return valA > valB ? 1 : valA < valB ? -1 : 0;
                } else {
                    return valA < valB ? 1 : valA > valB ? -1 : 0;
                }
            });
            
            sortedRuns.forEach(run => {
                const runRow = document.createElement('div');
                runRow.className = 'run-row';
                
                const isChecked = selectedRuns.some(r => r.domain === dom && r.timestamp === run.timestamp);
                
                runRow.innerHTML = `
                    <div>
                        <input type="checkbox" class="run-checkbox" data-domain="${dom}" data-timestamp="${run.timestamp}" ${isChecked ? 'checked' : ''}>
                    </div>
                    <div class="run-date">${formatDate(run.timestamp)}</div>
                    <div class="run-score"><span class="badge ${getScoreBadgeClass(run.overall_score)}">${run.overall_score}</span></div>
                    <div class="run-actions">
                        <button class="btn btn-secondary btn-icon load-run-btn" title="Dashboard anzeigen">
                            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                                <circle cx="12" cy="12" r="3"></circle>
                            </svg>
                        </button>
                        <button class="btn btn-secondary btn-icon reaudit-run-btn" title="Neu analysieren">
                            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"></path>
                            </svg>
                        </button>
                        <button class="btn btn-delete btn-icon delete-run-btn" title="Löschen">
                            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <polyline points="3 6 5 6 21 6"></polyline>
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                <line x1="10" y1="11" x2="10" y2="17"></line>
                                <line x1="14" y1="11" x2="14" y2="17"></line>
                            </svg>
                        </button>
                    </div>
                `;
                
                // Wire load button
                runRow.querySelector('.load-run-btn').addEventListener('click', () => {
                    loadFullReport(dom, run.timestamp);
                });
                
                // Wire reaudit button
                runRow.querySelector('.reaudit-run-btn').addEventListener('click', () => {
                    switchView('audit');
                    triggerAudit(run.url);
                });
                
                // Wire delete button
                runRow.querySelector('.delete-run-btn').addEventListener('click', async () => {
                    const message = `Möchtest du diesen Scan-Bericht vom ${formatDate(run.timestamp)} wirklich löschen?`;
                    if (await showCustomConfirm(message, "Bericht löschen?")) {
                        await deleteReport(dom, run.timestamp);
                    }
                });
                
                // Wire checkbox compare logic
                const checkbox = runRow.querySelector('.run-checkbox');
                checkbox.addEventListener('change', () => {
                    handleCheckboxChange(checkbox, dom, run.timestamp);
                });
                
                runsContainer.appendChild(runRow);
            });
            
            historyList.appendChild(group);
        });
    }

    // --- Pagination Helpers ---
    function renderPaginationNav(totalFiltered, totalPages) {
        const prevBtn = document.getElementById('prevPageBtn');
        const nextBtn = document.getElementById('nextPageBtn');
        const pageNumbers = document.getElementById('pageNumbers');
        
        if (!prevBtn || !nextBtn || !pageNumbers) return;
        
        prevBtn.disabled = currentPage === 1;
        nextBtn.disabled = currentPage === totalPages;
        
        pageNumbers.innerHTML = '';
        
        let startPage = Math.max(1, currentPage - 2);
        let endPage = Math.min(totalPages, currentPage + 2);
        
        if (startPage > 1) {
            pageNumbers.appendChild(createPageButton(1));
            if (startPage > 2) {
                const ellipsis = document.createElement('span');
                ellipsis.className = 'pagination-ellipsis';
                ellipsis.textContent = '...';
                ellipsis.style.color = 'var(--text-muted)';
                pageNumbers.appendChild(ellipsis);
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            pageNumbers.appendChild(createPageButton(i));
        }
        
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                const ellipsis = document.createElement('span');
                ellipsis.className = 'pagination-ellipsis';
                ellipsis.textContent = '...';
                ellipsis.style.color = 'var(--text-muted)';
                pageNumbers.appendChild(ellipsis);
            }
            pageNumbers.appendChild(createPageButton(totalPages));
        }
    }

    function createPageButton(pageNum) {
        const btn = document.createElement('button');
        btn.className = 'page-num-btn';
        if (pageNum === currentPage) btn.classList.add('active');
        btn.textContent = pageNum;
        btn.addEventListener('click', () => {
            currentPage = pageNum;
            filterAndRenderHistory();
        });
        return btn;
    }

    function formatDate(isoString) {
        if (!isoString) return '';
        const d = new Date(isoString);
        return d.toLocaleString('de-DE', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }

    function getScoreBadgeClass(score) {
        if (score >= 80) return 'badge-success';
        if (score >= 50) return 'badge-warning';
        return 'badge-danger';
    }

    async function loadFullReport(domain, timestamp) {
        try {
            const response = await fetch(`/api/report?domain=${encodeURIComponent(domain)}&timestamp=${encodeURIComponent(timestamp)}`);
            if (!response.ok) throw new Error('Fehler beim Laden der Berichtsdetails.');
            
            const report = await response.json();
            displayReport(report);
            switchView('audit');
        } catch (e) {
            alert(e.message);
        }
    }

    async function deleteReport(domain, timestamp) {
        try {
            const response = await fetch(`/api/report?domain=${encodeURIComponent(domain)}&timestamp=${encodeURIComponent(timestamp)}`, {
                method: 'DELETE'
            });
            if (!response.ok) throw new Error('Fehler beim Löschen des Berichts.');
            
            updateHistoryCount();
            loadHistory();
        } catch (e) {
            alert(e.message);
        }
    }

    async function deleteDomain(domain) {
        try {
            const response = await fetch(`/api/domain?domain=${encodeURIComponent(domain)}`, {
                method: 'DELETE'
            });
            if (!response.ok) throw new Error('Fehler beim Löschen der Domain.');
            
            updateHistoryCount();
            loadHistory();
        } catch (e) {
            alert(e.message);
        }
    }

    // === COMPARISON HANDLING (VERGLEICHS-LOGIK) ===

    function handleCheckboxChange(checkbox, domain, timestamp) {
        if (checkbox.checked) {
            if (selectedRuns.length >= 2) {
                // Uncheck and return if already 2 selected
                checkbox.checked = false;
                alert("Du kannst maximal 2 Berichte zeitgleich vergleichen.");
                return;
            }
            selectedRuns.push({ domain, timestamp });
        } else {
            selectedRuns = selectedRuns.filter(r => !(r.domain === domain && r.timestamp === timestamp));
        }
        
        updateCompareActionBar();
    }

    function updateCompareActionBar() {
        if (selectedRuns.length === 2) {
            compareActionsBar.style.display = 'flex';
            const run1 = selectedRuns[0];
            const run2 = selectedRuns[1];
            compareInfoText.textContent = `Fortschrittsvergleich bereit: ${run1.domain} (${formatDate(run1.timestamp).split(',')[0]}) mit (${formatDate(run2.timestamp).split(',')[0]}).`;
        } else {
            compareActionsBar.style.display = 'none';
        }
    }

    triggerCompareBtn.addEventListener('click', () => {
        if (selectedRuns.length === 2) {
            compareReports(selectedRuns[0], selectedRuns[1]);
        }
    });

    async function compareReports(runA, runB) {
        try {
            // Load both full reports
            const resA = await fetch(`/api/report?domain=${encodeURIComponent(runA.domain)}&timestamp=${encodeURIComponent(runA.timestamp)}`);
            const resB = await fetch(`/api/report?domain=${encodeURIComponent(runB.domain)}&timestamp=${encodeURIComponent(runB.timestamp)}`);
            
            if (!resA.ok || !resB.ok) throw new Error("Fehler beim Abrufen der Berichtsdaten für den Vergleich.");
            
            const repA = await resA.json();
            const repB = await resB.json();
            
            // Sort chronologically: Oldest is Old, Newest is New
            let oldRep, newRep;
            if (new Date(repA.timestamp) <= new Date(repB.timestamp)) {
                oldRep = repA;
                newRep = repB;
            } else {
                oldRep = repB;
                newRep = repA;
            }
            
            // Populate comparison page
            comparisonMeta.textContent = `Domänenvergleich für: ${oldRep.url}`;
            
            // Dates
            compDateOld.textContent = formatDate(oldRep.timestamp);
            compDateNew.textContent = formatDate(newRep.timestamp);
            
            // Scores Overall
            compScoreOld.textContent = oldRep.overall_score;
            compScoreNew.textContent = newRep.overall_score;
            
            const deltaScore = newRep.overall_score - oldRep.overall_score;
            updateDeltaBadge(compScoreDelta, deltaScore);
            
            // Subscores Details
            updateScoreRow(compSeoOld, compSeoNew, compSeoDelta, oldRep.scores.seo, newRep.scores.seo);
            updateScoreRow(compAeoOld, compAeoNew, compAeoDelta, oldRep.scores.aeo, newRep.scores.aeo);
            updateScoreRow(compSchemaOld, compSchemaNew, compSchemaDelta, oldRep.scores.schema, newRep.scores.schema);
            updateScoreRow(compEeatOld, compEeatNew, compEeatDelta, oldRep.scores.eeat, newRep.scores.eeat);
            
            const oldTextVal = oldRep.scores.hasOwnProperty('text') ? oldRep.scores.text : 0;
            const newTextVal = newRep.scores.hasOwnProperty('text') ? newRep.scores.text : 0;
            const compTextOld = document.getElementById('compTextOld');
            const compTextNew = document.getElementById('compTextNew');
            const compTextDelta = document.getElementById('compTextDelta');
            updateScoreRow(compTextOld, compTextNew, compTextDelta, oldTextVal, newTextVal);
            
            // Generate Changelog Lists (Improvements / Worsened checks)
            generateChangelog(oldRep, newRep);
            
            switchView('comparison');
            
        } catch (e) {
            alert(e.message);
        }
    }

    function updateDeltaBadge(element, val) {
        element.className = 'comp-delta-badge';
        if (val > 0) {
            element.textContent = `▲ +${val}`;
            element.classList.add('positive');
        } else if (val < 0) {
            element.textContent = `▼ ${val}`;
            element.classList.add('negative');
        } else {
            element.textContent = `0`;
            element.classList.add('neutral');
        }
    }

    function updateScoreRow(oldEl, newEl, deltaEl, oldVal, newVal) {
        oldEl.textContent = oldVal;
        newEl.textContent = newVal;
        
        const delta = newVal - oldVal;
        deltaEl.className = 'delta-inline';
        if (delta > 0) {
            deltaEl.textContent = `+${delta}`;
            deltaEl.classList.add('positive');
        } else if (delta < 0) {
            deltaEl.textContent = `${delta}`;
            deltaEl.classList.add('negative');
        } else {
            deltaEl.textContent = `0`;
            deltaEl.classList.add('neutral');
        }
    }

    function generateChangelog(oldReport, newReport) {
        compImprovedList.innerHTML = '';
        compWorsenedList.innerHTML = '';
        
        const improved = [];
        const worsened = [];
        
        // Helper to compile lists of audited IDs and status
        const oldChecks = extractChecksMap(oldReport);
        const newChecks = extractChecksMap(newReport);
        
        // Compare new checks with old checks
        Object.keys(newChecks).forEach(checkId => {
            const newStatus = newChecks[checkId].status;
            const oldStatus = oldChecks[checkId] ? oldChecks[checkId].status : null;
            const message = newChecks[checkId].message;
            
            if (oldStatus) {
                // If status improved (e.g. was danger/warning, now success; or was danger, now warning)
                if (statusWeight(newStatus) > statusWeight(oldStatus)) {
                    improved.push(`${checkId.toUpperCase()}: ${message} (Zuvor unzureichend)`);
                } 
                // If status worsened (e.g. was success, now warning/danger; or was warning, now danger)
                else if (statusWeight(newStatus) < statusWeight(oldStatus)) {
                    worsened.push(`${checkId.toUpperCase()}: ${message} (Verschlechterung)`);
                }
            } else {
                // New audit point implemented or detected
                if (newStatus === 'success') {
                    improved.push(`${checkId.toUpperCase()}: ${message}`);
                } else if (newStatus === 'danger' || newStatus === 'warning') {
                    worsened.push(`${checkId.toUpperCase()}: ${message}`);
                }
            }
        });
        
        // Render lists
        if (improved.length > 0) {
            improved.forEach(text => {
                const li = document.createElement('li');
                li.textContent = text;
                compImprovedList.appendChild(li);
            });
        } else {
            compImprovedList.innerHTML = '<li>Keine behobenen Warnungen oder Verbesserungen erfasst.</li>';
        }
        
        if (worsened.length > 0) {
            worsened.forEach(text => {
                const li = document.createElement('li');
                li.textContent = text;
                compWorsenedList.appendChild(li);
            });
        } else {
            compWorsenedList.innerHTML = '<li>Keine neuen Fehler oder Regressionen entdeckt. Gute Arbeit!</li>';
        }
    }

    function extractChecksMap(report) {
        const checks = {};
        
        // Pull details from all five dimensions
        const dimensions = ['seo', 'aeo', 'schema', 'eeat', 'text'];
        dimensions.forEach(dim => {
            const reportDetails = report.reports[dim] ? report.reports[dim].details : null;
            if (reportDetails) {
                reportDetails.forEach(detail => {
                    checks[detail.id] = {
                        status: detail.status,
                        message: detail.message
                    };
                });
            }
        });
        
        return checks;
    }

    function statusWeight(status) {
        if (status === 'success') return 3;
        if (status === 'warning') return 2;
        if (status === 'danger') return 1;
        return 0;
    }

    backToHistoryBtn.addEventListener('click', () => {
        switchView('history');
    });


    // === INTERACTIVE SCHEMA GENERATOR (FAQ) ===
    let faqCount = 1;

    addQuestionBtn.addEventListener('click', () => {
        faqCount++;
        const inputGroup = document.createElement('div');
        inputGroup.className = 'faq-input-group';
        inputGroup.innerHTML = `
            <div class="form-control-group">
                <label>Frage ${faqCount}</label>
                <input type="text" class="faq-question-input" placeholder="z. B. Welche Zahlungsarten gibt es?">
            </div>
            <div class="form-control-group">
                <label>Antwort ${faqCount}</label>
                <textarea class="faq-answer-input" rows="3" placeholder="z. B. Wir bieten Zahlung per PayPal, Kreditkarte und Lastschrift an."></textarea>
            </div>
            <button type="button" class="btn btn-secondary btn-sm remove-faq-btn" style="margin-top: 0.5rem; background-color: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.15); color: var(--accent-rose);">Entfernen</button>
        `;
        
        inputGroup.querySelector('.remove-faq-btn').addEventListener('click', () => {
            inputGroup.remove();
            reorderFaqLabels();
        });

        faqQuestionsContainer.appendChild(inputGroup);
    });

    function reorderFaqLabels() {
        const groups = faqQuestionsContainer.querySelectorAll('.faq-input-group');
        faqCount = groups.length;
        groups.forEach((group, idx) => {
            const num = idx + 1;
            group.querySelector('label:nth-of-type(1)').textContent = `Frage ${num}`;
            group.querySelectorAll('label')[1].textContent = `Antwort ${num}`;
        });
    }

    generateSchemaBtn.addEventListener('click', () => {
        const questions = faqQuestionsContainer.querySelectorAll('.faq-question-input');
        const answers = faqQuestionsContainer.querySelectorAll('.faq-answer-input');
        const mainEntity = [];
        
        for (let i = 0; i < questions.length; i++) {
            const qVal = questions[i].value.trim();
            const aVal = answers[i].value.trim();
            
            if (qVal && aVal) {
                mainEntity.push({
                    "@type": "Question",
                    "name": qVal,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": aVal
                    }
                });
            }
        }

        if (mainEntity.length === 0) {
            schemaOutputText.textContent = "// Bitte fülle mindestens eine Frage und Antwort aus.";
            return;
        }

        const faqSchema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": mainEntity
        };

        schemaOutputText.textContent = JSON.stringify(faqSchema, null, 2);
    });

    copySchemaBtn.addEventListener('click', () => {
        const code = schemaOutputText.textContent;
        if (code.startsWith('//')) return;
        
        navigator.clipboard.writeText(code).then(() => {
            const originalText = copySchemaBtn.textContent;
            copySchemaBtn.textContent = 'Kopiert!';
            copySchemaBtn.style.borderColor = 'var(--accent-emerald)';
            copySchemaBtn.style.color = 'var(--accent-emerald)';
            
            setTimeout(() => {
                copySchemaBtn.textContent = originalText;
                copySchemaBtn.style.borderColor = '';
                copySchemaBtn.style.color = '';
            }, 2000);
        });
    });

    // === CUSTOM CONFIRMATION DIALOG ===
    function showCustomConfirm(message, title = "Löschen bestätigen") {
        return new Promise((resolve) => {
            const modal = document.getElementById('customConfirmModal');
            const titleEl = document.getElementById('confirmModalTitle');
            const msgEl = document.getElementById('confirmModalMessage');
            const confirmBtn = document.getElementById('confirmModalConfirmBtn');
            const cancelBtn = document.getElementById('confirmModalCancelBtn');

            titleEl.textContent = title;
            msgEl.textContent = message;

            modal.style.display = 'flex';
            // Force reflow
            modal.offsetHeight;
            modal.classList.add('show');

            const cleanup = (value) => {
                modal.classList.remove('show');
                setTimeout(() => {
                    modal.style.display = 'none';
                }, 300);
                
                confirmBtn.removeEventListener('click', onConfirm);
                cancelBtn.removeEventListener('click', onCancel);
                modal.removeEventListener('click', onBackdropClick);
                document.removeEventListener('keydown', onKeyDown);
                
                resolve(value);
            };

            const onConfirm = () => cleanup(true);
            const onCancel = () => cleanup(false);
            const onBackdropClick = (e) => {
                if (e.target === modal) cleanup(false);
            };
            const onKeyDown = (e) => {
                if (e.key === 'Escape') cleanup(false);
            };

            confirmBtn.addEventListener('click', onConfirm);
            cancelBtn.addEventListener('click', onCancel);
            modal.addEventListener('click', onBackdropClick);
            document.addEventListener('keydown', onKeyDown);
        });
    }

    // === AUTO-TRIGGER FROM URL PARAMETER ===
    const urlParams = new URLSearchParams(window.location.search);
    const autoUrl = urlParams.get('url');
    if (autoUrl) {
        urlInput.value = autoUrl;
        triggerAudit(autoUrl);
    }
});
