import os
import re
import urllib.parse
from typing import Dict, Any, List, Optional
import httpx
from bs4 import BeautifulSoup

# List of high-authority domains for citation checks
HIGH_AUTHORITY_DOMAINS = [
    "wikipedia.org", "w3.org", "google.com", "microsoft.com", "ncbi.nlm.nih.gov", 
    "doi.org", "researchgate.net", "arxiv.org", "github.com", "statista.com",
    "bund.de", "europa.eu", "nature.com", "science.org", "destatis.de"
]

# Common German & English W-questions for heading scans
QUESTION_WORDS = [
    "wer", "was", "warum", "wie", "wo", "wann", "weshalb", "wieso", "wofür", "woher", "wohin",
    "who", "what", "why", "how", "where", "when", "which", "whose", "whom"
]

# Direct answer starters (German and English)
DIRECT_ANSWER_STARTERS = [
    "ist", "sind", "bedeutet", "bezeichnet", "definiert", "wird als", "kann als",
    "is", "are", "means", "refers to", "defines", "is defined as", "can be", "to do this"
]

def clean_text(text: str) -> str:
    """Helper to remove excessive whitespace and clean text."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

class SEOAnalyzer:
    def __init__(self, url: str, html_content: str, gemini_api_key: Optional[str] = None):
        self.url = url
        self.soup = BeautifulSoup(html_content, "html.parser")
        self.parsed_url = urllib.parse.urlparse(url)
        self.base_domain = self.parsed_url.netloc
        self.gemini_api_key = gemini_api_key

    def analyze(self) -> Dict[str, Any]:
        """Runs all audits and returns the full report."""
        seo_report = self._audit_traditional_seo()
        aeo_report = self._audit_aeo()
        schema_report = self._audit_schema()
        eeat_report = self._audit_eeat()
        text_report = self._audit_text_quality()

        # Calculate scores
        seo_score = seo_report["score"]
        aeo_score = aeo_report["score"]
        schema_score = schema_report["score"]
        eeat_score = eeat_report["score"]
        text_score = text_report["score"]

        overall_score = round(
            (seo_score * 0.20) +
            (aeo_score * 0.25) +
            (schema_score * 0.15) +
            (eeat_score * 0.20) +
            (text_score * 0.20)
        )

        # Collect overall recommendations
        successes = []
        optimizations = []
        criticals = []

        # Traditional SEO recommendations
        for item in seo_report["details"]:
            if item["status"] == "success":
                successes.append(f"SEO: {item['message']}")
            elif item["status"] == "warning":
                optimizations.append(f"SEO: {item['message']}")
            elif item["status"] == "danger":
                criticals.append(f"SEO: {item['message']}")

        # AEO recommendations
        for item in aeo_report["details"]:
            if item["status"] == "success":
                successes.append(f"KI: {item['message']}")
            elif item["status"] == "warning":
                optimizations.append(f"KI: {item['message']}")
            elif item["status"] == "danger":
                criticals.append(f"KI: {item['message']}")

        # Schema recommendations
        for item in schema_report["details"]:
            if item["status"] == "success":
                successes.append(f"Schema: {item['message']}")
            elif item["status"] == "warning":
                optimizations.append(f"Schema: {item['message']}")
            elif item["status"] == "danger":
                criticals.append(f"Schema: {item['message']}")

        # EEAT recommendations
        for item in eeat_report["details"]:
            if item["status"] == "success":
                successes.append(f"E-E-A-T: {item['message']}")
            elif item["status"] == "warning":
                optimizations.append(f"E-E-A-T: {item['message']}")
            elif item["status"] == "danger":
                criticals.append(f"E-E-A-T: {item['message']}")

        # Text Quality recommendations
        for item in text_report["details"]:
            if item["status"] == "success":
                successes.append(f"Text: {item['message']}")
            elif item["status"] == "warning":
                optimizations.append(f"Text: {item['message']}")
            elif item["status"] == "danger":
                criticals.append(f"Text: {item['message']}")

        return {
            "url": self.url,
            "overall_score": overall_score,
            "scores": {
                "seo": seo_score,
                "aeo": aeo_score,
                "schema": schema_score,
                "eeat": eeat_score,
                "text": text_score
            },
            "reports": {
                "seo": seo_report,
                "aeo": aeo_report,
                "schema": schema_report,
                "eeat": eeat_report,
                "text": text_report
            },
            "summary": {
                "critical": criticals,
                "optimization": optimizations,
                "success": successes
            }
        }

    def _audit_traditional_seo(self) -> Dict[str, Any]:
        score = 100
        details = []

        # 1. Page Title
        title_tag = self.soup.find("title")
        if not title_tag:
            score -= 20
            details.append({
                "id": "missing_title",
                "status": "danger",
                "message": "Der Seitentitel (<title>) fehlt komplett.",
                "info": "Füge ein prägnantes <title>-Tag im <head> ein (optimal 50-60 Zeichen)."
            })
        else:
            title_text = title_tag.get_text().strip()
            title_len = len(title_text)
            if title_len == 0:
                score -= 20
                details.append({
                    "id": "empty_title",
                    "status": "danger",
                    "message": "Der Seitentitel (<title>) ist leer.",
                    "info": "Ein leerer Seitentitel erschwert das Ranking. Definiere einen treffenden Titel."
                })
            elif title_len < 30:
                score -= 5
                details.append({
                    "id": "short_title",
                    "status": "warning",
                    "message": f"Der Seitentitel ist sehr kurz ({title_len} Zeichen).",
                    "info": "Ein optimaler Titel hat zwischen 30 und 60 Zeichen und enthält die wichtigsten Keywords."
                })
            elif title_len > 65:
                score -= 5
                details.append({
                    "id": "long_title",
                    "status": "warning",
                    "message": f"Der Seitentitel ist zu lang ({title_len} Zeichen).",
                    "info": "Titel mit mehr als 60-65 Zeichen werden in den Google-Suchergebnissen oft abgeschnitten (...)."
                })
            else:
                details.append({
                    "id": "title_ok",
                    "status": "success",
                    "message": f"Seitentitel ist optimal optimiert ({title_len} Zeichen).",
                    "info": f"Titel: '{title_text}'"
                })

        # 2. Meta Description
        meta_desc = self.soup.find("meta", attrs={"name": "description"})
        if not meta_desc:
            score -= 15
            details.append({
                "id": "missing_desc",
                "status": "danger",
                "message": "Die Meta-Beschreibung fehlt.",
                "info": "Die Meta-Beschreibung erhöht die Klickrate (CTR). Erstelle eine Beschreibung mit 120-160 Zeichen."
            })
        else:
            desc_text = meta_desc.get("content", "").strip()
            desc_len = len(desc_text)
            if desc_len == 0:
                score -= 15
                details.append({
                    "id": "empty_desc",
                    "status": "danger",
                    "message": "Die Meta-Beschreibung ist leer.",
                    "info": "Fülle das content-Attribut des Meta-Tags mit einer aussagekräftigen Zusammenfassung."
                })
            elif desc_len < 100:
                score -= 5
                details.append({
                    "id": "short_desc",
                    "status": "warning",
                    "message": f"Die Meta-Beschreibung ist zu kurz ({desc_len} Zeichen).",
                    "info": "Eine optimale Meta-Beschreibung liegt zwischen 110 und 160 Zeichen."
                })
            elif desc_len > 165:
                score -= 5
                details.append({
                    "id": "long_desc",
                    "status": "warning",
                    "message": f"Die Meta-Beschreibung ist zu lang ({desc_len} Zeichen).",
                    "info": "Beschreibungen über 160 Zeichen werden in Suchergebnissen abgeschnitten."
                })
            else:
                details.append({
                    "id": "desc_ok",
                    "status": "success",
                    "message": f"Meta-Beschreibung hat eine optimale Länge ({desc_len} Zeichen).",
                    "info": f"Beschreibung: '{desc_text}'"
                })

        # 3. Heading Structure (H1 check)
        h1s = self.soup.find_all("h1")
        if len(h1s) == 0:
            score -= 15
            details.append({
                "id": "missing_h1",
                "status": "danger",
                "message": "Keine H1-Überschrift gefunden.",
                "info": "Jede Seite sollte genau eine Hauptüberschrift <h1> haben, um der Suchmaschine das Hauptthema anzuzeigen."
            })
        elif len(h1s) > 1:
            score -= 10
            details.append({
                "id": "multiple_h1",
                "status": "warning",
                "message": f"Mehrere H1-Überschriften gefunden ({len(h1s)} H1s).",
                "info": "Empfohlen ist genau eine H1-Überschrift pro Seite. Nutze H2-H4 für Zwischenüberschriften."
            })
        else:
            details.append({
                "id": "h1_ok",
                "status": "success",
                "message": "Genau eine H1-Überschrift vorhanden.",
                "info": f"H1: '{clean_text(h1s[0].get_text())}'"
            })

        # 4. Images Alt Attributes
        images = self.soup.find_all("img")
        if images:
            missing_alt_count = 0
            for img in images:
                if not img.get("alt") or len(img.get("alt").strip()) == 0:
                    missing_alt_count += 1
            
            if missing_alt_count > 0:
                missing_ratio = (missing_alt_count / len(images)) * 100
                score_loss = min(15, round(missing_ratio * 0.15))
                score -= score_loss
                details.append({
                    "id": "missing_alt",
                    "status": "warning" if missing_ratio < 50 else "danger",
                    "message": f"{missing_alt_count} von {len(images)} Bildern haben kein Alt-Attribut ({round(missing_ratio)}% ohne Alt-Text).",
                    "info": "Alt-Texte sind entscheidend für die Barrierefreiheit und Bildersuche. Füge beschreibende alt-Attribute hinzu."
                })
            else:
                details.append({
                    "id": "alt_ok",
                    "status": "success",
                    "message": f"Alle {len(images)} Bilder besitzen ein Alt-Attribut.",
                    "info": "Perfekt für Barrierefreiheit und Google-Bildersuche."
                })
        else:
            details.append({
                "id": "no_images",
                "status": "success",
                "message": "Keine Bilder auf der Seite gefunden.",
                "info": "Keine Alt-Attribut-Prüfung erforderlich."
            })

        # 5. Link structure
        links = self.soup.find_all("a", href=True)
        internal_count = 0
        external_count = 0
        for l in links:
            href = l.get("href")
            parsed_href = urllib.parse.urlparse(href)
            if not parsed_href.netloc or parsed_href.netloc == self.base_domain:
                internal_count += 1
            else:
                external_count += 1

        details.append({
            "id": "links_info",
            "status": "success",
            "message": f"Linkstruktur analysiert: {internal_count} interne Links, {external_count} externe Links.",
            "info": "Eine gesunde Mischung aus internen (Themencluster) und externen Links (Referenzen) stärkt das SEO."
        })

        return {
            "score": max(0, score),
            "details": details,
            "data": {
                "title": title_tag.get_text().strip() if title_tag else "",
                "description": meta_desc.get("content", "").strip() if meta_desc else "",
                "h1_count": len(h1s),
                "image_count": len(images),
                "internal_links": internal_count,
                "external_links": external_count
            }
        }

    def _audit_aeo(self) -> Dict[str, Any]:
        """Audits page content for Answer Engine Optimization (AEO) & AI Search Overviews."""
        score = 100
        details = []
        qa_pairs = []

        # Find all headings (H1, H2, H3) and analyze if they pose questions, and if the following element is a direct answer
        headings = self.soup.find_all(["h1", "h2", "h3"])
        question_headings_count = 0
        aeo_optimized_count = 0

        for h in headings:
            h_text = clean_text(h.get_text())
            h_text_lower = h_text.lower()
            
            # Check if this heading is a question
            is_question = False
            if h_text.endswith("?"):
                is_question = True
            else:
                # Check if it starts or contains any common question word
                words = re.findall(r'\w+', h_text_lower)
                if any(w in QUESTION_WORDS for w in words):
                    is_question = True

            if is_question:
                question_headings_count += 1
                
                # Find the next paragraph or sibling element
                sibling = h.find_next_sibling()
                # Skip to next sibling if it's empty or whitespace
                while sibling and sibling.name not in ["p", "ul", "ol", "div"]:
                    sibling = sibling.find_next_sibling()

                if sibling:
                    answer_text = clean_text(sibling.get_text())
                    words_in_answer = len(answer_text.split())
                    
                    # Checks for direct answers:
                    # 1. Length rule (40 to 70 words is optimal for AI models to extract as a direct quote/summary)
                    is_length_optimal = 30 <= words_in_answer <= 80
                    
                    # 2. Semantic directness: Does the text start with a direct definition/response word?
                    # Check first few words
                    first_few_words = " ".join(answer_text.split()[:5]).lower()
                    has_direct_starter = any(starter in first_few_words for starter in DIRECT_ANSWER_STARTERS)
                    # Also check if it directly states a fact rather than beating around the bush
                    
                    status = "optimized"
                    rating = "Sehr Gut"
                    feedback = "Dieser Absatz ist hervorragend als direktes Antwort-Snippet für KI-Modelle strukturiert."

                    if not is_length_optimal:
                        status = "needs_work"
                        rating = "Verbesserungswürdig"
                        feedback = f"Die Wortanzahl ({words_in_answer} Wörter) ist ungeeignet. Versuche die direkte Antwort prägnanter zu fassen (optimal 40-60 Wörter)."
                    elif not has_direct_starter:
                        status = "needs_work"
                        rating = "Mittelmäßig"
                        feedback = "Die Antwort beginnt nicht direkt. Starte den ersten Satz des Absatzes präzise mit dem Subjekt und einer direkten Definition (z.B. '[Thema] ist...')."
                    
                    if status == "optimized":
                        aeo_optimized_count += 1

                    qa_pairs.append({
                        "heading": h_text,
                        "heading_type": h.name.upper(),
                        "answer_preview": answer_text[:200] + ("..." if len(answer_text) > 200 else ""),
                        "word_count": words_in_answer,
                        "rating": rating,
                        "status": status,
                        "feedback": feedback
                    })
                else:
                    qa_pairs.append({
                        "heading": h_text,
                        "heading_type": h.name.upper(),
                        "answer_preview": "[Kein Textabsatz direkt nach dieser Überschrift gefunden]",
                        "word_count": 0,
                        "rating": "Kritisch",
                        "status": "danger",
                        "feedback": "Es wurde kein Textblock direkt nach der Frage gefunden. KI-Modelle können diese Frage so nicht beantworten."
                    })

        # Calculate AEO scores based on results
        if question_headings_count == 0:
            score -= 30
            details.append({
                "id": "no_questions",
                "status": "warning",
                "message": "Keine fragebasierten Überschriften gefunden.",
                "info": "AI Overviews basieren meist auf konkreten Nutzerfragen. Integriere FAQ-Bereiche oder wandle Zwischenüberschriften in Fragen um (z. B. 'Wie funktioniert X?' statt 'X Funktion')."
            })
        else:
            optimization_rate = (aeo_optimized_count / question_headings_count) * 100
            if optimization_rate < 50:
                score -= 15
                details.append({
                    "id": "low_aeo_optimization",
                    "status": "warning",
                    "message": f"Nur {aeo_optimized_count} von {question_headings_count} Q&A-Blöcken sind KI-optimiert ({round(optimization_rate)}%).",
                    "info": "Optimiere die Absätze direkt nach deinen Frage-Überschriften. Halte sie kurz (40-60 Wörter) und beginne mit einer direkten Definition."
                })
            else:
                details.append({
                    "id": "high_aeo_optimization",
                    "status": "success",
                    "message": f"Hohe AEO-Optimierung: {aeo_optimized_count} von {question_headings_count} Q&A-Blöcken sind KI-optimiert.",
                    "info": "Die Struktur deiner Antworten begünstigt eine direkte Zitierung in KI-Suchergebnissen."
                })

        # Check general readability (Average sentence length)
        body_text = clean_text(self.soup.get_text())
        sentences = [s.strip() for s in re.split(r'[.!?]+', body_text) if s.strip()]
        
        if sentences:
            total_words = len(body_text.split())
            avg_sentence_len = total_words / len(sentences)
            
            if avg_sentence_len > 22:
                score -= 10
                details.append({
                    "id": "complex_readability",
                    "status": "warning",
                    "message": f"Sehr lange Sätze im Durchschnitt ({round(avg_sentence_len, 1)} Wörter/Satz).",
                    "info": "KI-Modelle bevorzugen leicht verdauliche, prägnante Sätze. Reduziere Schachtelsätze und halte die Satzlänge unter 18 Wörtern."
                })
            else:
                details.append({
                    "id": "good_readability",
                    "status": "success",
                    "message": f"Gute Lesbarkeit: Durchschnittlich {round(avg_sentence_len, 1)} Wörter pro Satz.",
                    "info": "Klare und verständliche Satzstrukturen erleichtern KI-Crawlern die Informationsextraktion."
                })
        else:
            avg_sentence_len = 0

        # Build full heading outline for structure visualization
        heading_outline = []
        for h in self.soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            heading_outline.append({
                "level": int(h.name[1]),
                "tag": h.name.upper(),
                "text": clean_text(h.get_text()),
                "is_question": h.get_text().strip().endswith("?") or any(w in h.get_text().lower() for w in QUESTION_WORDS)
            })

        return {
            "score": max(0, score),
            "details": details,
            "qa_pairs": qa_pairs,
            "heading_outline": heading_outline,
            "data": {
                "question_headings": question_headings_count,
                "aeo_optimized": aeo_optimized_count,
                "avg_sentence_len": round(avg_sentence_len, 1)
            }
        }

    def _audit_schema(self) -> Dict[str, Any]:
        """Audits Schema.org / Structured Data JSON-LD markup."""
        score = 0
        details = []
        found_schemas = []
        
        schema_scripts = self.soup.find_all("script", type="application/ld+json")
        
        # Base score starts at 0, increases for each correct schema setup up to 100
        if not schema_scripts:
            details.append({
                "id": "no_schema",
                "status": "danger",
                "message": "Keine strukturierten Daten (JSON-LD Schema Markup) gefunden.",
                "info": "Schema-Daten sind das Fundament für KI-Modelle, um Produkte, FAQs und Abläufe fehlerfrei zu verstehen. Implementiere FAQPage oder Product Schema."
            })
            score = 0
        else:
            score += 40  # Points for having schema at all
            import json
            
            for script in schema_scripts:
                try:
                    data = json.loads(script.string or "")
                    
                    # Handle lists of schemas
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and "@type" in item:
                                found_schemas.append(item)
                    elif isinstance(data, dict):
                        if "@graph" in data:
                            for item in data["@graph"]:
                                if isinstance(item, dict) and "@type" in item:
                                    found_schemas.append(item)
                        elif "@type" in data:
                            found_schemas.append(data)
                except Exception as e:
                    # Broken JSON
                    score -= 10
                    details.append({
                        "id": "broken_json_ld",
                        "status": "danger",
                        "message": "Fehlerhaftes JSON-LD Markup entdeckt.",
                        "info": f"Ein JSON-LD-Script enthält Syntaxfehler und kann von Suchmaschinen nicht gelesen werden: {str(e)[:100]}"
                    })

            # Check for AI-critical schemas
            types_found = []
            for s in found_schemas:
                t = s.get("@type")
                if isinstance(t, list):
                    types_found.extend(t)
                elif isinstance(t, str):
                    types_found.append(t)

            ai_critical_types = ["FAQPage", "HowTo", "Product", "Article", "Recipe", "LocalBusiness"]
            matched_critical = [t for t in types_found if t in ai_critical_types]

            if matched_critical:
                score += min(60, len(matched_critical) * 20)  # Up to 60 additional points
                details.append({
                    "id": "critical_schemas_found",
                    "status": "success",
                    "message": f"KI-relevante Schema-Typen gefunden: {', '.join(matched_critical)}.",
                    "info": "Diese Auszeichnungen helfen Google AI Overviews, deine Daten präzise zuzuordnen."
                })
            else:
                details.append({
                    "id": "no_critical_schemas",
                    "status": "warning",
                    "message": "Es wurden strukturierte Daten gefunden, aber keine KI-kritischen Typen (wie FAQPage, HowTo, Product oder Article).",
                    "info": "Füge spezifischere Markups hinzu, um die Sichtbarkeit in KI-Suchergebnissen zu erhöhen."
                })

            details.append({
                "id": "schemas_count",
                "status": "success",
                "message": f"Insgesamt {len(found_schemas)} Schema-Objekte erfolgreich extrahiert.",
                "info": "Nutze das Schema Explorer Tab, um die Struktur im Detail zu analysieren."
            })

        return {
            "score": min(100, max(0, score)),
            "details": details,
            "found_schemas": found_schemas,
            "data": {
                "schema_count": len(found_schemas),
                "has_schema": len(schema_scripts) > 0
            }
        }

    def _audit_eeat(self) -> Dict[str, Any]:
        """Audits E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) factors."""
        score = 100
        details = []
        trust_links_found = []

        # 1. Trust Signals (Legal pages, contact, imprint)
        links = self.soup.find_all("a", href=True)
        trust_patterns = {
            "impressum": ["impressum", "imprint", "legal-notice", "anbieterkennzeichnung"],
            "datenschutz": ["datenschutz", "privacy", "privacy-policy", "data-protection"],
            "kontakt": ["kontakt", "contact", "schreibe-uns", "support"],
            "ueber_uns": ["ueber-uns", "about", "about-us", "team", "wer-wir-sind"]
        }
        
        detected_trust = {key: False for key in trust_patterns}
        
        for l in links:
            href = l.get("href", "").lower()
            text = l.get_text().lower()
            
            for key, patterns in trust_patterns.items():
                if not detected_trust[key]:
                    if any(p in href or p in text for p in patterns):
                        detected_trust[key] = True
                        trust_links_found.append({"type": key, "url": href, "text": clean_text(l.get_text())})

        missing_trust = [k for k, found in detected_trust.items() if not found]
        if missing_trust:
            score -= (len(missing_trust) * 10)
            details.append({
                "id": "missing_trust_signals",
                "status": "danger" if len(missing_trust) >= 2 else "warning",
                "message": f"Fehlende Vertrauensseiten: {', '.join(missing_trust).replace('_', ' ')}.",
                "info": "Google bewertet die Vertrauenswürdigkeit (Trust) höher, wenn Seiten wie Impressum, Datenschutz und Kontakt leicht auffindbar sind."
            })
        else:
            details.append({
                "id": "trust_signals_ok",
                "status": "success",
                "message": "Alle wichtigen Vertrauensseiten (Impressum, Datenschutz, Kontakt, Über uns) wurden erkannt.",
                "info": "Hervorragendes Signal für das E-E-A-T-Vertrauenskriterium."
            })

        # 2. Author signals (expert author verification)
        author_element = self.soup.find(lambda tag: tag.name in ["span", "a", "div", "p"] and 
                                      (tag.get("class") and any("author" in c.lower() for c in tag.get("class")) or
                                       tag.get("id") and "author" in tag.get("id").lower() or
                                       "autor" in tag.get_text().lower() or "author" in tag.get_text().lower()))
        
        if not author_element:
            score -= 15
            details.append({
                "id": "missing_author",
                "status": "warning",
                "message": "Keine Autorenbox oder Autoren-Metadaten im HTML-Text gefunden.",
                "info": "KI-Modelle bevorzugen Inhalte, die eindeutigen Experten zugeordnet werden können. Binde eine Autorenbox mit Kurzbiografie ein."
            })
        else:
            author_name = clean_text(author_element.get_text())[:100]
            details.append({
                "id": "author_found",
                "status": "success",
                "message": f"Möglicher Autor im Content erkannt: '{author_name}'",
                "info": "Hilft Google und KI-Suchmaschinen, das Expertise-Kriterium zuzuordnen."
            })

        # 3. Facts, Citations and References (external scientific or high authority links)
        citations_count = 0
        authority_citations = []
        
        for l in links:
            href = l.get("href", "")
            parsed_href = urllib.parse.urlparse(href)
            domain = parsed_href.netloc.lower()
            
            if any(auth_domain in domain for auth_domain in HIGH_AUTHORITY_DOMAINS):
                citations_count += 1
                authority_citations.append(href)

        # Check for numbers representing statistics or percentages in text
        body_text = self.soup.get_text()
        stat_matches = re.findall(r'\b\d+\s*%|\b\d+\s*(?:Prozent|percent)\b', body_text)
        
        if citations_count == 0:
            score -= 10
            details.append({
                "id": "no_citations",
                "status": "warning",
                "message": "Keine externen Fachzitate oder hoch-autoritativen Referenzlinks gefunden.",
                "info": "KI-Suchmaschinen bevorzugen faktengestützte und belegte Texte. Verlinke auf Studien, Regierungsquellen, Wikipedia oder Fachartikel."
            })
        else:
            details.append({
                "id": "citations_found",
                "status": "success",
                "message": f"{citations_count} hoch-autoritative Quellenangaben/Zitate gefunden.",
                "info": f"Referenz-URLs: {', '.join(authority_citations[:3])}"
            })

        if stat_matches:
            details.append({
                "id": "stats_found",
                "status": "success",
                "message": f"Fakten- und Statistikindikatoren im Text gefunden ({len(stat_matches)} Vorkommen).",
                "info": f"Erkannte Werte: {', '.join(stat_matches[:4])}"
            })
        else:
            score -= 5
            details.append({
                "id": "no_stats",
                "status": "warning",
                "message": "Keine statistischen oder numerischen Datenpunkte gefunden.",
                "info": "Fakten und Zahlen untermauern die Glaubwürdigkeit und machen Inhalte zitierfähiger für KI-Zusammenfassungen."
            })

        return {
            "score": max(0, score),
            "details": details,
            "trust_links": trust_links_found,
            "data": {
                "detected_trust_pages": [k for k, v in detected_trust.items() if v],
                "authority_citations_count": citations_count,
                "has_author_info": author_element is not None,
                "stat_indicators_count": len(stat_matches)
            }
        }

    def _get_clean_body_text(self) -> str:
        # Clone soup to avoid modifying original
        soup_copy = BeautifulSoup(str(self.soup), "html.parser")
        for tag in soup_copy(["script", "style", "nav", "footer", "header", "noscript", "head", "iframe"]):
            tag.decompose()
        text = soup_copy.get_text(separator=" ")
        return clean_text(text)

    def _audit_text_quality(self) -> Dict[str, Any]:
        """Audits the quality of webpage text: Klarheit, Originalität, Emotionale Wirkung, Konkretheit."""
        text = self._get_clean_body_text()
        
        # Word count
        words = text.split()
        word_count = len(words)
        
        # Default empty report if text is too short
        if word_count < 10:
            return {
                "score": 0,
                "is_ai_analyzed": False,
                "details": [],
                "data": {
                    "word_count": word_count,
                    "klarheit": {"score": 1, "explanation": "Zu wenig Text zum Analysieren.", "recommendations": ["Füge der Seite mehr Inhalt hinzu."]},
                    "originalitaet": {"score": 1, "explanation": "Zu wenig Text zum Analysieren.", "recommendations": ["Füge der Seite mehr Inhalt hinzu."]},
                    "emotion": {"score": 1, "explanation": "Zu wenig Text zum Analysieren.", "recommendations": ["Füge der Seite mehr Inhalt hinzu."]},
                    "konkretheit": {"score": 1, "explanation": "Zu wenig Text zum Analysieren.", "recommendations": ["Füge der Seite mehr Inhalt hinzu."]}
                }
            }
            
        # Determine if we use Gemini API or Local Heuristics
        api_key = self.gemini_api_key or os.environ.get("GEMINI_API_KEY")
        
        if api_key:
            try:
                import json
                import httpx
                
                # Prompt to Gemini
                prompt = (
                    "Analysiere den folgenden Webseitentext auf vier Qualitätskriterien:\n"
                    "1. KLARHEIT (Ist die Sprache verständlich, direkt, ohne unnötige Schachtelsätze?)\n"
                    "2. ORIGINALITÄT (Gibt es frischen, einzigartigen Inhalt oder ist der Text voller leerer Floskeln und Corporate Buzzwords?)\n"
                    "3. EMOTIONALE WIRKUNG (Ist der Text ansprechend, packend, baut er Verbindung auf oder ist er staubtrocken?)\n"
                    "4. KONKRETHEIT (Gibt es konkrete Fakten, Zahlen, Daten und Beispiele oder bleibt alles schwammig und abstrakt?)\n\n"
                    "Bewerte jedes Kriterium auf einer Skala von 1 (sehr schlecht) bis 5 (hervorragend).\n"
                    "Gib für jedes Kriterium einen Score (Integer 1-5), eine präzise Erklärung (1-2 Sätze auf Deutsch) und 2 konkrete Optimierungsempfehlungen (auf Deutsch) an.\n\n"
                    "Formatierte deine Antwort AUSSCHLIESSLICH als gültiges JSON-Objekt mit genau dieser Struktur:\n"
                    "{\n"
                    "  \"klarheit\": {\n"
                    "    \"score\": 4,\n"
                    "    \"explanation\": \"Erklärung für Klarheit...\",\n"
                    "    \"recommendations\": [\"Empfehlung 1\", \"Empfehlung 2\"]\n"
                    "  },\n"
                    "  \"originalitaet\": {\n"
                    "    \"score\": 3,\n"
                    "    \"explanation\": \"Erklärung für Originalität...\",\n"
                    "    \"recommendations\": [\"Empfehlung 1\", \"Empfehlung 2\"]\n"
                    "  },\n"
                    "  \"emotion\": {\n"
                    "    \"score\": 2,\n"
                    "    \"explanation\": \"Erklärung für Emotion...\",\n"
                    "    \"recommendations\": [\"Empfehlung 1\", \"Empfehlung 2\"]\n"
                    "  },\n"
                    "  \"konkretheit\": {\n"
                    "    \"score\": 5,\n"
                    "    \"explanation\": \"Erklärung für Konkretheit...\",\n"
                    "    \"recommendations\": [\"Empfehlung 1\", \"Empfehlung 2\"]\n"
                    "  }\n"
                    "}\n\n"
                    "Hier ist der Webseitentext:\n"
                    f"{text[:6000]}"
                )
                
                # Make HTTP call to Gemini
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "responseMimeType": "application/json"
                    }
                }
                
                with httpx.Client(timeout=90.0) as client:
                    response = client.post(url, json=payload)
                    response.raise_for_status()
                    res_json = response.json()
                    
                    ai_text = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                    res_data = json.loads(ai_text)
                    
                    required_keys = ["klarheit", "originalitaet", "emotion", "konkretheit"]
                    if all(k in res_data for k in required_keys):
                        total_score = round(
                            (res_data["klarheit"]["score"] + 
                             res_data["originalitaet"]["score"] + 
                             res_data["emotion"]["score"] + 
                             res_data["konkretheit"]["score"]) / 20 * 100
                        )
                        
                        details = []
                        criteria_names = {
                            "klarheit": "Klarheit",
                            "originalitaet": "Originalität",
                            "emotion": "Emotionale Wirkung",
                            "konkretheit": "Konkretheit"
                        }
                        
                        for key, name in criteria_names.items():
                            val = res_data[key]
                            score_val = val["score"]
                            
                            if score_val >= 4:
                                status = "success"
                                msg = f"Text-Bewertung ({name}): Sehr gut ({score_val}/5). {val['explanation']}"
                            elif score_val == 3:
                                status = "warning"
                                msg = f"Text-Bewertung ({name}): Optimierungspotenzial ({score_val}/5). {val['explanation']}"
                            else:
                                status = "danger"
                                msg = f"Text-Bewertung ({name}): Dringender Handlungsbedarf ({score_val}/5). {val['explanation']}"
                                
                            details.append({
                                "id": f"text_{key}",
                                "status": status,
                                "message": msg,
                                "info": " | ".join(val["recommendations"])
                            })
                            
                        return {
                            "score": total_score,
                            "is_ai_analyzed": True,
                            "details": details,
                            "data": {
                                "word_count": word_count,
                                "klarheit": res_data["klarheit"],
                                "originalitaet": res_data["originalitaet"],
                                "emotion": res_data["emotion"],
                                "konkretheit": res_data["konkretheit"]
                            }
                        }
            except Exception as e:
                print(f"[WARNING] Gemini API-Fehler: {str(e)}. Nutze lokale Heuristik als Fallback.")
                
        # --- LOCAL HEURISTICS FALLBACK ---
        # 1. Klarheit (Clarity)
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        avg_sentence_len = word_count / len(sentences) if sentences else 0
        
        if avg_sentence_len <= 14:
            klarheit_score = 5
            klarheit_exp = f"Hervorragende Klarheit. Die durchschnittliche Satzlänge liegt bei sehr lesbaren {round(avg_sentence_len, 1)} Wörtern."
            klarheit_recs = ["Behalte diesen klaren und prägnanten Schreibstil bei.", "Achte darauf, Fachbegriffe bei Erstnennung kurz zu erläutern."]
        elif avg_sentence_len <= 18:
            klarheit_score = 4
            klarheit_exp = f"Gute Klarheit mit durchschnittlich {round(avg_sentence_len, 1)} Wörtern pro Satz."
            klarheit_recs = ["Vermeide vereinzelte Schachtelsätze.", "Verwende aktive statt passive Formulierungen."]
        elif avg_sentence_len <= 22:
            klarheit_score = 3
            klarheit_exp = f"Mäßige Klarheit. Mit im Schnitt {round(avg_sentence_len, 1)} Wörtern pro Satz sind einige Passagen schwer lesbar."
            klarheit_recs = ["Teile lange Sätze (über 20 Wörter) konsequent in zwei eigenständige Sätze auf.", "Reduziere Füllwörter wie 'eigentlich', 'gewissermaßen', 'insbesondere'."]
        elif avg_sentence_len <= 26:
            klarheit_score = 2
            klarheit_exp = f"Schwere Lesbarkeit. Sätze sind mit durchschnittlich {round(avg_sentence_len, 1)} Wörtern zu verschachtelt."
            klarheit_recs = ["Kürze Nebensatz-Konstruktionen und Nominalstil.", "Setze auf klare Subjekt-Verb-Objekt-Strukturen."]
        else:
            klarheit_score = 1
            klarheit_exp = f"Kritische Klarheit. Extrem lange Schachtelsätze ({round(avg_sentence_len, 1)} Wörter/Satz) behindern das Leseverständnis massiv."
            klarheit_recs = ["Schreibe die Texte grundlegend um und fokussiere dich auf kurze Hauptsätze.", "Nutze Bulletpoints für komplexe Aufzählungen."]

        # 2. Originalität (Originality)
        buzzwords = [
            "innovativ", "synergie", "synergien", "kundenorientiert", "ganzheitlich", "einzigartig", 
            "mehrwert", "optimal", "disruption", "disruptiv", "lösungsorientiert", "modernst", 
            "marktführer", "revolutionär", "zukunftssicher", "passion", "leidenschaft", "dna",
            "exzellenz", "führend", "agil", "transformieren", "nachhaltig", "best-in-class"
        ]
        
        text_lower = text.lower()
        found_buzzwords = []
        for bw in buzzwords:
            matches = len(re.findall(r'\b' + bw + r'\b', text_lower))
            if matches > 0:
                found_buzzwords.append((bw, matches))
                
        total_buzzwords = sum(count for bw, count in found_buzzwords)
        buzzword_density = (total_buzzwords / word_count) * 100 if word_count > 0 else 0
        
        unique_words = len(set(words))
        ttr = unique_words / word_count if word_count > 0 else 0
        
        if buzzword_density < 0.8 and ttr > 0.45:
            orig_score = 5
            orig_exp = "Sehr hohe Originalität. Der Text verzichtet fast vollständig auf abgedroschene Phrasen und glänzt mit abwechslungsreichem Vokabular."
            orig_recs = ["Behalte diesen individuellen Ausdruck bei.", "Nutze weiterhin kreative Analogien anstelle von Branchen-Floskeln."]
        elif buzzword_density < 1.5 and ttr > 0.38:
            orig_score = 4
            orig_exp = "Gute Originalität. Nur vereinzelte Buzzwords trüben den insgesamt eigenständigen Eindruck."
            orig_recs = ["Ersetze Standard-Begriffe wie 'innovativ' durch konkrete Beschreibungen Ihrer Arbeitsweise.", "Vermeide leere Versprechungen und untermauere Behauptungen."]
        elif buzzword_density < 2.5 or ttr > 0.32:
            orig_score = 3
            orig_exp = f"Mäßige Originalität. Es wurden {total_buzzwords} typische Marketing-Floskeln gefunden. Der Stil wirkt stellenweise generisch."
            orig_recs = ["Reduzieren Sie leere Worthülsen (z.B. '" + "', '".join([bw for bw, _ in found_buzzwords[:2]]) + "').", "Beschreiben Sie Ihren echten Nutzen statt Werbe-Klischees."]
        elif buzzword_density < 4.0:
            orig_score = 2
            orig_exp = f"Geringe Originalität. Der Text enthält viele Phrasen ({round(buzzword_density, 1)}% Buzzword-Dichte) und klingt wie viele Konkurrenzseiten."
            orig_recs = ["Formulieren Sie Marketing-Standard-Sätze komplett um.", "Erklären Sie Ihr Angebot so, wie Sie es einem Freund in Alltagssprache erklären würden."]
        else:
            orig_score = 1
            orig_exp = f"Sehr geringe Originalität. Extrem hohe Buzzword-Dichte ({round(buzzword_density, 1)}%). Der Inhalt wirkt platt und unpersönlich."
            orig_recs = ["Entfernen Sie Werbe-Clichés radikal.", "Schreiben Sie aus der Perspektive echter Kundenprobleme, anstatt sich selbst zu beweihräuchern."]

        # 3. Emotionale Wirkung (Emotional Impact)
        address_words = ["du", "dir", "dein", "deine", "dich", "sie", "ihnen", "ihr", "ihre", "wir", "uns", "unser", "unsere"]
        address_count = sum(len(re.findall(r'\b' + aw + r'\b', text_lower)) for aw in address_words)
        address_density = (address_count / word_count) * 100 if word_count > 0 else 0
        
        emotional_words = [
            "erfolg", "erfolgreich", "begeistern", "sicher", "einfach", "sparen", "entdecken", "garantiert",
            "schutz", "schützen", "lösen", "lösung", "wachsen", "wachstum", "hilfe", "helfen", "gewinnen",
            "effizient", "spitzenleistung", "traum", "vision", "gemeinsam", "partnerschaft", "vertrauen",
            "sicherheit", "risiko", "verlust", "angst", "freiheit", "freuen", "freude"
        ]
        emotional_count = sum(len(re.findall(r'\b' + ew + r'\b', text_lower)) for ew in emotional_words)
        emotional_density = (emotional_count / word_count) * 100 if word_count > 0 else 0
        
        if emotional_density > 2.0 and address_density > 2.0:
            emot_score = 5
            emot_exp = "Starke emotionale Ansprache. Der Leser wird direkt eingebunden und durch aktivierende Wörter emotional abgeholt."
            emot_recs = ["Verwende diesen packenden Tonfall für Call-to-Actions.", "Achte darauf, die emotionale Ansprache nicht übertrieben wirken zu lassen."]
        elif emotional_density > 1.2 and address_density > 1.0:
            emot_score = 4
            emot_exp = "Gute emotionale Wirkung. Die Texte sprechen den Leser an und erzeugen ein grundlegendes Interesse."
            emot_recs = ["Setze noch gezielter emotionale Verstärker ein.", "Verbinde Features mit dem emotionalen Nutzen für den Kunden (Benefits statt Features)."]
        elif emotional_density > 0.5 or address_density > 0.5:
            emot_score = 3
            emot_exp = "Mäßige emotionale Wirkung. Der Text ist eher sachlich-neutral formuliert und baut wenig emotionale Verbindung auf."
            emot_recs = ["Sprechen Sie den Leser direkter an (Nutzen Sie 'Du' oder 'Sie' statt unpersönlicher 'man'-Formulierungen).", "Erklären Sie, welches Gefühl das gelöste Problem beim Kunden hinterlässt."]
        else:
            emot_score = 2
            emot_exp = "Schwache emotionale Wirkung. Der Schreibstil ist trocken und distanziert."
            emot_recs = ["Integrieren Sie aktive Verben statt passive Beschreibungen.", "Verwenden Sie Storytelling-Elemente, um das Interesse zu wecken."]

        # 4. Konkretheit (Concreteness)
        stat_indicators = len(re.findall(r'\b\d+\b|\b\d+\s*%|€|\$|CHF|Prozent|percent', text))
        stat_density = (stat_indicators / word_count) * 100 if word_count > 0 else 0
        
        if stat_density > 2.0:
            konkr_score = 5
            konkr_exp = f"Sehr konkreter Text. Viele Zahlen, Fakten oder Datensätze ({stat_indicators} Vorkommen) untermauern die Behauptungen."
            konkr_recs = ["Achte darauf, dass die Textlesbarkeit durch die vielen Zahlen nicht beeinträchtigt wird.", "Visualisiere Datenpunkte idealerweise in Form von Grafiken."]
        elif stat_density > 1.0:
            konkr_score = 4
            konkr_exp = f"Gute Konkretheit. Argumente werden durch relevante Zahlen und Fakten ({stat_indicators} Funde) gestützt."
            konkr_recs = ["Prüfe, ob du noch konkrete Fallstudien verlinken kannst.", "Ergänze Prozentangaben oder Zeiträume, wo immer sinnvoll."]
        elif stat_density > 0.3:
            konkr_score = 3
            konkr_exp = f"Mäßige Konkretheit. Der Text bleibt stellenweise vage und nennt wenige harte Fakten (nur {stat_indicators} Indikatoren)."
            konkr_recs = ["Ersetzen Sie schwammige Formulierungen wie 'viele Kunden' durch konkrete Zahlen (z.B. 'über 150 Unternehmen').", "Nennen Sie konkrete Fristen, Prozentwerte oder Messergebnisse."]
        else:
            konkr_score = 2
            konkr_exp = "Geringe Konkretheit. Behauptungen werden ohne jegliche Belege oder genaue Daten aufgestellt."
            konkr_recs = ["Untermauern Sie Ihre Expertise mit messbaren Erfolgen (z.B. '+30% Umsatz', 'in 4 Tagen').", "Geben Sie konkrete Beispiele aus der Praxis statt abstrakter Theorien."]

        total_score = round((klarheit_score + orig_score + emot_score + konkr_score) / 20 * 100)
        
        details = []
        criteria_names = {
            "klarheit": ("Klarheit", klarheit_score, klarheit_exp, klarheit_recs),
            "originalitaet": ("Originalität", orig_score, orig_exp, orig_recs),
            "emotion": ("Emotionale Wirkung", emot_score, emot_exp, emot_recs),
            "konkretheit": ("Konkretheit", konkr_score, konkr_exp, konkr_recs)
        }
        
        for key, (name, score_val, exp, recs) in criteria_names.items():
            if score_val >= 4:
                status = "success"
                msg = f"Text-Bewertung ({name}): Sehr gut ({score_val}/5). {exp}"
            elif score_val == 3:
                status = "warning"
                msg = f"Text-Bewertung ({name}): Optimierungspotenzial ({score_val}/5). {exp}"
            else:
                status = "danger"
                msg = f"Text-Bewertung ({name}): Dringender Handlungsbedarf ({score_val}/5). {exp}"
                
            details.append({
                "id": f"text_{key}",
                "status": status,
                "message": msg,
                "info": " | ".join(recs)
            })
            
        return {
            "score": total_score,
            "is_ai_analyzed": False,
            "details": details,
            "data": {
                "word_count": word_count,
                "klarheit": {"score": klarheit_score, "explanation": klarheit_exp, "recommendations": klarheit_recs},
                "originalitaet": {"score": orig_score, "explanation": orig_exp, "recommendations": orig_recs},
                "emotion": {"score": emot_score, "explanation": emot_exp, "recommendations": emot_recs},
                "konkretheit": {"score": konkr_score, "explanation": konkr_exp, "recommendations": konkr_recs}
            }
        }

async def fetch_and_analyze(url: str, gemini_api_key: Optional[str] = None) -> Dict[str, Any]:
    """Helper that fetches a URL and executes the analysis."""
    # Ensure URL has a scheme
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    try:
        # Try with SSL verification enabled first
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            response = await client.get(url, headers=headers)
    except Exception as e:
        # Fallback: Retry with SSL verification disabled
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=15.0, verify=False) as client:
                response = await client.get(url, headers=headers)
        except httpx.ConnectError as ce:
            raise Exception(f"Verbindungsfehler: Die Domain konnte nicht erreicht werden ({str(ce)}). Prüfe die Schreibweise.")
        except httpx.TimeoutException as te:
            raise Exception(f"Timeout: Die Webseite hat nicht rechtzeitig geantwortet ({str(te)}).")
        except Exception as inner_e:
            raise Exception(f"Fehler beim Laden der Webseite: {str(inner_e)}")
    except httpx.TimeoutException as te:
        raise Exception(f"Timeout: Die Webseite hat nicht rechtzeitig geantwortet ({str(te)}).")
    except Exception as e:
        raise Exception(f"Fehler beim Laden der Webseite: {str(e)}")

    if response.status_code != 200:
        raise Exception(f"HTTP Fehlerstatus {response.status_code}")
    
    html_content = response.text
    
    # Run parser and analyzer
    analyzer = SEOAnalyzer(url, html_content, gemini_api_key=gemini_api_key)
    return analyzer.analyze()
