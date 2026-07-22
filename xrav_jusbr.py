#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de geração de script para extração de dados do Jusbrasil.

Este módulo pode ser executado como script principal ou importado como módulo.
O nome do arquivo não interfere no funcionamento do código.
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TerminalColors:
    """Define cores para formatação de texto no terminal."""
    
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RED = '\033[91m'
    RESET = '\033[0m'


class ScriptGenerator:
    """Gerador de script JavaScript para extração de dados do Jusbrasil."""
    
    def __init__(self) -> None:
        """Inicializa o gerador de script."""
        self._script_template = self._build_script_template()
    
    def _build_script_template(self) -> str:
        """
        Constrói o template do script JavaScript.
        
        Returns:
            str: Template completo do script JavaScript
        """
        return r'''
(function() {
    'use strict';
    
    // ============================================================
    // CONFIGURAÇÃO INICIAL
    // ============================================================
    
    // A variável global usa um nome único para evitar conflitos
    if (window.__XRAV_INSTANCE__) {
        console.warn('XRAV já está em execução. Removendo instância anterior...');
        window.__XRAV_INSTANCE__.destroy();
        delete window.__XRAV_INSTANCE__;
    }
    
    (function(){
        var link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';
        link.integrity = 'sha512-iecdLmaskl7CVkqkXNQ/ZH/XLlvWZOJyj7Yy7tcenmpD1ypASozpmT/E0iPtmFIB46ZmdtAc9eNBvH0H/ZpiBw==';
        link.crossOrigin = 'anonymous';
        document.head.appendChild(link);
    })();
    
    // ============================================================
    // ESTADO DA APLICAÇÃO
    // ============================================================
    
    var X = window.__XRAV_INSTANCE__ || {};
    X.running = false;
    X.results = [];
    X.people = [];
    X.stop = false;
    X.name = '';
    X.cpfMask = '';
    X.delay = 3000;
    X.processing = false;
    X.startTime = null;
    X.endTime = null;
    X.stats = { 
        total: 0, 
        withCPF: 0, 
        withoutCPF: 0, 
        companies: 0, 
        states: {}, 
        ages: [] 
    };
    
    // Método para limpeza
    X.destroy = function() {
        var ui = document.getElementById('xrav-ui');
        if (ui) ui.remove();
        console.log('XRAV destruído com sucesso');
    };
    
    window.__XRAV_INSTANCE__ = X;
    
    // ============================================================
    // FUNÇÕES AUXILIARES
    // ============================================================
    
    function detect_name_from_page() {
        var name = '';
        var h1_elements = document.querySelectorAll('h1');
        
        for (var i = 0; i < h1_elements.length; i++) {
            var h1 = h1_elements[i];
            var h1_text = h1.textContent || '';
            
            if (h1_text.includes('Consulta processual')) {
                var strongs = h1.querySelectorAll('strong');
                for (var j = 0; j < strongs.length; j++) {
                    var strong_text = strongs[j].textContent.trim();
                    if (strong_text && strong_text.length > 3) {
                        return strong_text;
                    }
                }
                
                var match = h1_text.match(/sobre\s+([^<]+)/);
                if (match && match[1]) {
                    name = match[1].trim();
                    if (name.length > 3) return name;
                }
            }
        }
        
        var inputs = document.querySelectorAll('input[type="search"], input[name="q"]');
        for (var k = 0; k < inputs.length; k++) {
            if (inputs[k].value && inputs[k].value.trim().length > 3) {
                return inputs[k].value.trim();
            }
        }
        
        var url_params = new URLSearchParams(window.location.search);
        var q_param = url_params.get('q');
        if (q_param) {
            name = decodeURIComponent(q_param).replace(/\+/g, ' ');
            if (name.length > 3) return name;
        }
        
        var selectors = ['h1', 'h2', 'h3', '[data-testid="header-name"]'];
        for (var s = 0; s < selectors.length; s++) {
            var elements = document.querySelectorAll(selectors[s]);
            for (var e = 0; e < elements.length; e++) {
                var text = elements[e].textContent.trim();
                var words = text.split(/\s+/);
                if (words.length >= 2 && text.length < 100 && text.length > 5) {
                    var generic_terms = ['resultados', 'busca', 'consulta', 'processual', 'sobre'];
                    var is_generic = false;
                    for (var g = 0; g < generic_terms.length; g++) {
                        if (text.toLowerCase().includes(generic_terms[g])) {
                            is_generic = true;
                            break;
                        }
                    }
                    if (!is_generic) return text;
                }
            }
        }
        
        return '';
    }
    
    function auto_detect_name() {
        var name_input = document.getElementById('xrav-name');
        if (!name_input) return;
        
        var detected_name = detect_name_from_page();
        if (detected_name) {
            name_input.value = detected_name;
            name_input.style.borderColor = '#00ff88';
            name_input.style.boxShadow = '0 0 20px rgba(0,255,136,0.2)';
            name_input.style.background = 'rgba(0,255,136,0.05)';
            X.name = detected_name;
            
            var log_el = document.getElementById('xrav-log');
            if (log_el) {
                var line = document.createElement('div');
                line.style.cssText = 'padding:4px 0;border-bottom:1px solid rgba(0,255,136,0.05);font-size:12px;font-family:"Courier New",monospace;';
                line.innerHTML = '<span style="color:#00ff88;">NOME DETECTADO: </span><span style="color:#ffffff;font-weight:bold;">' + detected_name + '</span>';
                log_el.appendChild(line);
                log_el.scrollTop = log_el.scrollHeight;
            }
        } else {
            name_input.placeholder = 'Digite o nome (detecção falhou)';
            name_input.style.borderColor = 'rgba(255,68,68,0.3)';
            name_input.style.background = 'rgba(255,68,68,0.05)';
            
            var log_el = document.getElementById('xrav-log');
            if (log_el) {
                var line = document.createElement('div');
                line.style.cssText = 'padding:4px 0;border-bottom:1px solid rgba(255,68,68,0.05);font-size:12px;font-family:"Courier New",monospace;';
                line.innerHTML = '<span style="color:#ff4444;">NÃO DETECTADO - Informe manualmente</span>';
                log_el.appendChild(line);
                log_el.scrollTop = log_el.scrollHeight;
            }
        }
    }
    
    function validate_cpf(cpf) {
        if (cpf.length !== 11 || !/^\d{11}$/.test(cpf)) return false;
        if (/^(\d)\1{10}$/.test(cpf)) return false;
        
        var sum = 0;
        for (var i = 0; i < 9; i++) {
            sum += parseInt(cpf.charAt(i)) * (10 - i);
        }
        var remainder = sum % 11;
        var digit1 = remainder < 2 ? 0 : 11 - remainder;
        if (parseInt(cpf.charAt(9)) !== digit1) return false;
        
        sum = 0;
        for (var i = 0; i < 10; i++) {
            sum += parseInt(cpf.charAt(i)) * (11 - i);
        }
        remainder = sum % 11;
        var digit2 = remainder < 2 ? 0 : 11 - remainder;
        return parseInt(cpf.charAt(10)) === digit2;
    }
    
    function format_cpf(cpf) {
        return cpf.substring(0,3) + '.' + cpf.substring(3,6) + '.' + cpf.substring(6,9) + '-' + cpf.substring(9,11);
    }
    
    function sleep(ms) {
        return new Promise(function(resolve) { 
            setTimeout(resolve, ms); 
        });
    }
    
    function format_time(ms) {
        var seconds = Math.floor(ms / 1000);
        var minutes = Math.floor(seconds / 60);
        seconds = seconds % 60;
        return minutes > 0 ? minutes + 'm ' + seconds + 's' : seconds + 's';
    }
    
    function generate_cpfs(mask, limit) {
        limit = limit || 100;
        var clean = mask.replace(/[^0-9X*]/g,'').toUpperCase().replace(/\*/g,'X');
        if (clean.length !== 11) {
            alert('Mascara invalida! Use: ***.123.123-**');
            return [];
        }
        
        var x_pos = [];
        for (var i = 0; i < clean.length; i++) {
            if (clean[i] === 'X') x_pos.push(i);
        }
        
        if (x_pos.length === 0) return validate_cpf(clean) ? [clean] : [];
        
        var digits = [];
        for (var i = 0; i < 11; i++) {
            if (x_pos.indexOf(i) !== -1) {
                digits.push(i === 0 ? [1,2,3,4,5,6,7,8,9] : [0,1,2,3,4,5,6,7,8,9]);
            } else {
                digits.push([parseInt(clean[i])]);
            }
        }
        
        var candidates = [];
        function combine(idx, current) {
            if (idx === digits.length) {
                var cpf = current.join('');
                if (validate_cpf(cpf)) candidates.push(cpf);
                return;
            }
            for (var i = 0; i < digits[idx].length; i++) {
                var new_current = current.slice();
                new_current.push(digits[idx][i]);
                combine(idx + 1, new_current);
            }
        }
        combine(0, []);
        
        return candidates.length > limit ? candidates.slice(0, limit) : candidates;
    }
    
    // ============================================================
    // FUNÇÕES DE EXTRAÇÃO DE DADOS
    // ============================================================
    
    function extract_data(html) {
        var data = {};
        var match;
        
        if ((match = html.match(/<h1[^>]*data-testid="header-name"[^>]*>(.*?)<\/h1>/))) {
            data.name = match[1].replace(/<[^>]+>/g,'').trim();
        }
        if (!data.name) {
            var h1_match = html.match(/<h1[^>]*>(.*?)<\/h1>/);
            if (h1_match) data.name = h1_match[1].replace(/<[^>]+>/g,'').trim();
        }
        
        if ((match = html.match(/CPF\s*<!--\s*-->\s*(\*{3}\.\d{3}\.\d{3}-\*{2})/))) {
            data.cpf = match[1];
        }
        if (!data.cpf) {
            var cpf_patterns = [
                /\b(\d{3}\.\d{3}\.\d{3}-\d{2})\b/,
                /\b(\*{3}\.\d{3}\.\d{3}-\*{2})\b/,
                /CPF[:\s]+([\d*.]{3,})/
            ];
            for (var p = 0; p < cpf_patterns.length; p++) {
                if ((match = html.match(cpf_patterns[p]))) {
                    data.cpf = match[1];
                    break;
                }
            }
        }
        
        var age_patterns = [
            /(\d+)\s*anos?/i,
            /idade[:\s]+(\d+)/i,
            /<span[^>]*>(\d+)\s*anos?/i
        ];
        for (var a = 0; a < age_patterns.length; a++) {
            if ((match = html.match(age_patterns[a]))) {
                data.age = match[1];
                break;
            }
        }
        
        var state_patterns = [
            /([A-Z]{2})\s*[•●]/,
            /[•●]\s*([A-Z]{2})/,
            /estado[:\s]+([A-Z]{2})/i,
            /uf[:\s]+([A-Z]{2})/i
        ];
        for (var s = 0; s < state_patterns.length; s++) {
            if ((match = html.match(state_patterns[s]))) {
                data.state = match[1];
                break;
            }
        }
        
        var companies = [];
        var company_patterns = [
            /entity-summary[^>]*>(.*?)<\/div>\s*<\/div>\s*<\/div>/gs,
            /(?:empresa|company)[^>]*>(.*?)<\/div>/gi,
            /card[^>]*>(.*?)<\/div>/gi
        ];
        
        var cards = [];
        for (var i = 0; i < company_patterns.length; i++) {
            var matches = html.match(company_patterns[i]);
            if (matches && matches.length > 0) {
                cards = matches;
                break;
            }
        }
        
        if (cards && cards.length > 0) {
            for (var i = 0; i < Math.min(cards.length, 20); i++) {
                var card = cards[i];
                var company = {};
                
                var name_match = card.match(/>([^<]{3,50})<\/[a-z]/);
                if (name_match) company.name = name_match[1].trim();
                
                var cnpj_match = card.match(/\b(\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2})\b/);
                if (cnpj_match) company.cnpj = cnpj_match[1];
                
                var state_match = card.match(/\b([A-Z]{2})\b/);
                if (state_match && state_match[1].length === 2) company.state = state_match[1];
                
                if (company.name && company.name.length > 2) companies.push(company);
            }
        }
        data.companies = companies;
        return data;
    }
    
    function detect_results() {
        var results = [];
        var links = document.querySelectorAll('a[href*="/nome/"]');
        var processed = new Set();
        
        for (var i = 0; i < links.length; i++) {
            var link = links[i];
            var href = link.getAttribute('href');
            
            if (!href || !href.includes('/cpf-')) continue;
            if (processed.has(href)) continue;
            processed.add(href);
            
            var full_link = href;
            if (!href.startsWith('http')) full_link = 'https://www.jusbrasil.com.br' + href;
            
            var name = '';
            var text = link.textContent.trim();
            if (text && text.length > 2 && text.length < 100) {
                name = text;
            } else {
                var parent = link.parentElement;
                var spans = parent ? parent.querySelectorAll('span') : [];
                for (var s = 0; s < spans.length; s++) {
                    var span_text = spans[s].textContent.trim();
                    if (span_text && span_text.length > 2 && span_text.length < 80) {
                        name = span_text;
                        break;
                    }
                }
            }
            
            if (full_link && name) {
                results.push({
                    link: full_link,
                    name: name || 'N/I',
                    age: '',
                    state: '',
                    element: link
                });
            }
        }
        
        if (results.length === 0) {
            var cards = document.querySelectorAll('[class*="card"][class*="summary"]');
            for (var c = 0; c < cards.length; c++) {
                var card = cards[c];
                var link_el = card.querySelector('a[href*="/nome/"]');
                if (!link_el) continue;
                
                var href = link_el.getAttribute('href');
                if (!href || processed.has(href)) continue;
                processed.add(href);
                
                var full_link = href;
                if (!href.startsWith('http')) full_link = 'https://www.jusbrasil.com.br' + href;
                
                var name = link_el.textContent.trim() || 'N/I';
                results.push({
                    link: full_link,
                    name: name,
                    age: '',
                    state: '',
                    element: link_el
                });
            }
        }
        
        return results;
    }
    
    // ============================================================
    // FUNÇÕES DE PROCESSAMENTO
    // ============================================================
    
    async function fetch_profile(link) {
        try {
            var response = await fetch(link, {
                credentials: 'include',
                headers: {
                    'Accept': 'text/html',
                    'Accept-Language': 'pt-BR,pt;q=0.9',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache',
                    'User-Agent': navigator.userAgent
                }
            });
            if (!response.ok) return null;
            var html = await response.text();
            await sleep(500);
            return extract_data(html);
        } catch (error) {
            return null;
        }
    }
    
    async function process_results(results, cpf_mask, delay) {
        X.processing = true;
        var found = false, total = results.length, target = null;
        X.startTime = Date.now();
        X.stats = { total: 0, withCPF: 0, withoutCPF: 0, companies: 0, states: {}, ages: [] };
        
        log_message('═══════════════════════════════════════════════', '#335533');
        log_message('INICIANDO SCAN', '#00ff88', '<i class="fas fa-search"></i>');
        log_message('ALVOS: ' + total, '#00ff88', '<i class="fas fa-bullseye"></i>');
        log_message('MASCARA CPF: ' + cpf_mask, '#ffd43b', '<i class="fas fa-id-card"></i>');
        log_message('───────────────────────────────────────────────', '#335533');
        
        for (var i = 0; i < total; i++) {
            if (X.stop) {
                log_message('SCAN ABORTADO PELO USUARIO', '#ff4444', '<i class="fas fa-stop"></i>');
                break;
            }
            
            var res = results[i];
            var progress = '[' + String(i + 1).padStart(3, ' ') + '/' + String(total).padStart(3, ' ') + ']';
            log_message(progress + ' SCAN: ' + res.name, '#4dabf7', '<i class="fas fa-user"></i>');
            
            var data = await fetch_profile(res.link);
            if (data) {
                var person = {
                    name: data.name || res.name,
                    link: res.link,
                    cpf: data.cpf,
                    age: data.age || res.age,
                    state: data.state || res.state,
                    companies: data.companies || []
                };
                X.people.push(person);
                X.stats.total++;
                person.cpf ? X.stats.withCPF++ : X.stats.withoutCPF++;
                if (person.companies.length) X.stats.companies += person.companies.length;
                if (person.state) {
                    if (!X.stats.states[person.state]) X.stats.states[person.state] = 0;
                    X.stats.states[person.state]++;
                }
                if (person.age) X.stats.ages.push(person.age);
                
                var indent = '     ';
                log_message(indent + '├─ NOME: ' + person.name, '#ffffff');
                if (person.cpf) {
                    log_message(indent + '├─ CPF: ' + person.cpf, '#ffd43b');
                    var clean_mask = cpf_mask.replace(/[^0-9X*]/g,'').toUpperCase().replace(/\*/g,'X');
                    var clean_cpf = person.cpf.replace(/[^0-9X*]/g,'').toUpperCase().replace(/\*/g,'X');
                    if (clean_mask === clean_cpf) {
                        log_message(indent + '├─ MATCH ENCONTRADO!', '#51cf66', '<i class="fas fa-check"></i>');
                        found = true;
                        target = person;
                        X.results.push(person);
                    }
                }
                if (person.age) log_message(indent + '├─ IDADE: ' + person.age, '#4dabf7');
                if (person.state) log_message(indent + '├─ UF: ' + person.state, '#4dabf7');
                if (person.link) log_message(indent + '├─ LINK: ' + person.link, '#868e96');
                
                if (person.companies.length) {
                    log_message(indent + '└─ EMPRESAS:', '#ff6b6b');
                    for (var j = 0; j < person.companies.length; j++) {
                        var company = person.companies[j];
                        var prefix = (j === person.companies.length - 1) ? '   └─' : '   ├─';
                        var msg = prefix + ' ' + company.name + (company.legal && company.legal !== company.name ? ' (' + company.legal + ')' : '');
                        log_message(indent + '   ' + msg, '#ffd43b');
                        if (company.cnpj) log_message(indent + '      └─ CNPJ: ' + company.cnpj, '#4dabf7');
                        if (company.state) log_message(indent + '         └─ UF: ' + company.state, '#4dabf7');
                    }
                } else {
                    log_message(indent + '└─ EMPRESAS: NENHUMA', '#868e96');
                }
                log_message('');
                if (found) break;
            } else {
                log_message('     FALHA NA REQUISIÇÃO', '#ff4444', '<i class="fas fa-times"></i>');
            }
            if (i < total - 1 && !X.stop) await sleep(delay);
        }
        
        X.endTime = Date.now();
        var total_time = X.endTime - X.startTime;
        X.stats.time = total_time;
        X.stats.timeFmt = format_time(total_time);
        
        log_message('═══════════════════════════════════════════════', '#335533');
        log_message('ESTATISTICAS', '#ffd43b', '<i class="fas fa-chart-bar"></i>');
        log_message('───────────────────────────────────────────────', '#335533');
        log_message('TEMPO: ' + X.stats.timeFmt, '#ffffff');
        log_message('SCANEADOS: ' + X.stats.total, '#ffffff');
        log_message('COM CPF: ' + X.stats.withCPF, '#51cf66');
        log_message('SEM CPF: ' + X.stats.withoutCPF, '#ff6b6b');
        log_message('EMPRESAS: ' + X.stats.companies, '#ffd43b');
        
        var states = Object.keys(X.stats.states);
        if (states.length) {
            log_message('UFs ENCONTRADAS:', '#4dabf7');
            for (var k = 0; k < states.length; k++) {
                var state = states[k];
                var count = X.stats.states[state];
                var bar = '';
                for (var b = 0; b < Math.min(count, 15); b++) bar += '█';
                log_message('  └─ ' + state + ': ' + count + ' ' + bar, '#ffffff');
            }
        }
        if (X.stats.ages.length) {
            var age_count = {};
            for (var a = 0; a < X.stats.ages.length; a++) {
                var age = X.stats.ages[a];
                if (!age_count[age]) age_count[age] = 0;
                age_count[age]++;
            }
            var age_keys = Object.keys(age_count);
            if (age_keys.length) {
                log_message('IDADES:', '#4dabf7');
                for (var a2 = 0; a2 < age_keys.length; a2++) {
                    var age = age_keys[a2];
                    var count = age_count[age];
                    var bar = '';
                    for (var b2 = 0; b2 < Math.min(count, 15); b2++) bar += '█';
                    log_message('  └─ ' + age + ' anos: ' + count + ' ' + bar, '#ffffff');
                }
            }
        }
        log_message('═══════════════════════════════════════════════', '#335533');
        
        if (found && target) {
            log_message('', '#51cf66');
            log_message('ALVO ENCONTRADO!', '#51cf66', '<i class="fas fa-trophy"></i>');
            log_message('═══════════════════════════════════════════════', '#ffd43b');
            log_message('DADOS DO ALVO:', '#ffd43b', '<i class="fas fa-user"></i>');
            log_message('───────────────────────────────────────────────', '#335533');
            log_message('  ├─ NOME: ' + target.name, '#ffffff');
            if (target.cpf) log_message('  ├─ CPF: ' + target.cpf, '#ffd43b');
            if (target.age) log_message('  ├─ IDADE: ' + target.age, '#4dabf7');
            if (target.state) log_message('  ├─ UF: ' + target.state, '#4dabf7');
            if (target.link) log_message('  ├─ LINK: ' + target.link, '#868e96');
            if (target.companies.length) {
                log_message('  └─ EMPRESAS:', '#ff6b6b');
                for (var e = 0; e < target.companies.length; e++) {
                    var company = target.companies[e];
                    var prefix = (e === target.companies.length - 1) ? '     └─' : '     ├─';
                    var msg = prefix + ' ' + company.name + (company.legal && company.legal !== company.name ? ' (' + company.legal + ')' : '');
                    log_message('     ' + msg, '#ffd43b');
                    if (company.cnpj) log_message('        └─ CNPJ: ' + company.cnpj, '#4dabf7');
                    if (company.state) log_message('           └─ UF: ' + company.state, '#4dabf7');
                }
            }
            log_message('═══════════════════════════════════════════════', '#ffd43b');
            update_status('ALVO ENCONTRADO!', 'success');
        } else if (!X.stop) {
            log_message('');
            log_message('ALVO NÃO ENCONTRADO', '#ff4444', '<i class="fas fa-times"></i>');
        }
        
        X.processing = false;
        X.running = false;
        if (!found) update_status('PRONTO');
        var button = document.getElementById('xrav-btn');
        if (button) {
            button.innerHTML = '<i class="fas fa-play"></i> INICIAR';
            button.style.background = '#20c997';
        }
    }
    
    // ============================================================
    // FUNÇÕES DE LOG E INTERFACE
    // ============================================================
    
    function log_message(message, color, icon) {
        var element = document.getElementById('xrav-log');
        var count = document.getElementById('xrav-log-count');
        if (!element) return;
        
        var line = document.createElement('div');
        line.style.cssText = 'padding:4px 0;border-bottom:1px solid rgba(0,255,136,0.03);font-size:12px;font-family:"Courier New",monospace;line-height:1.4;';
        
        if (icon) {
            var span = document.createElement('span');
            span.innerHTML = icon;
            span.style.cssText = 'margin-right:8px;display:inline-block;width:18px;text-align:center;';
            line.appendChild(span);
        }
        
        var text = document.createElement('span');
        if (color) text.style.color = color;
        text.textContent = message;
        line.appendChild(text);
        
        element.appendChild(line);
        element.scrollTop = element.scrollHeight;
        if (count) count.textContent = element.children.length + ' linhas';
        
        while (element.children.length > 500) {
            element.removeChild(element.firstChild);
        }
    }
    
    function update_status(message, type) {
        var element = document.getElementById('xrav-status');
        if (!element) return;
        
        var colors = { running: '#ff6b6b', success: '#51cf66', idle: '#20c997' };
        var bg_colors = { running: 'rgba(255,107,107,0.08)', success: 'rgba(81,207,102,0.08)', idle: 'rgba(32,201,153,0.05)' };
        var color = type === 'running' ? colors.running : type === 'success' ? colors.success : colors.idle;
        var bg = type === 'running' ? bg_colors.running : type === 'success' ? bg_colors.success : bg_colors.idle;
        
        element.innerHTML = '<i class="fas fa-circle" style="color:' + color + ';font-size:8px;margin-right:8px;"></i> ' + message;
        element.style.borderColor = color;
        element.style.color = color;
        element.style.background = bg;
    }
    
    function clear_log() {
        var element = document.getElementById('xrav-log');
        var count = document.getElementById('xrav-log-count');
        if (element) element.innerHTML = '';
        if (count) count.textContent = '0 linhas';
        X.people = [];
        X.results = [];
        X.stats = { total: 0, withCPF: 0, withoutCPF: 0, companies: 0, states: {}, ages: [] };
    }
    
    // ============================================================
    // FUNÇÕES DE EXPORTAÇÃO
    // ============================================================
    
    function export_txt() {
        if (!X.people.length) {
            alert('Sem dados para exportar!');
            return;
        }
        
        var text = '';
        var separator = '═══════════════════════════════════════════════════════════\n';
        var divider = '───────────────────────────────────────────────────────────\n';
        
        text += separator + '  XRAV JUSBR - RELATÓRIO DE INVESTIGAÇÃO\n' + separator;
        text += '  DATA: ' + new Date().toLocaleString() + '\n';
        text += '  NOME: ' + X.name + '\n';
        text += '  MASCARA CPF: ' + X.cpfMask + '\n';
        text += '  SCANEADOS: ' + X.people.length + '\n';
        if (X.stats.timeFmt) text += '  TEMPO: ' + X.stats.timeFmt + '\n';
        text += separator + '\n';
        
        text += '📊 ESTATÍSTICAS\n' + divider;
        text += '  👤 SCANEADOS: ' + X.stats.total + '\n';
        text += '  🔢 COM CPF: ' + X.stats.withCPF + '\n';
        text += '  ❓ SEM CPF: ' + X.stats.withoutCPF + '\n';
        text += '  🏢 EMPRESAS: ' + X.stats.companies + '\n';
        
        var states = Object.keys(X.stats.states);
        if (states.length) {
            text += '  📍 UFs:\n';
            for (var k = 0; k < states.length; k++) {
                text += '     └─ ' + states[k] + ': ' + X.stats.states[states[k]] + '\n';
            }
        }
        
        text += '\n👤 PESSOAS ENCONTRADAS\n' + divider;
        for (var i = 0; i < X.people.length; i++) {
            var person = X.people[i];
            var match = false;
            if (person.cpf) {
                var mask1 = X.cpfMask.replace(/[^0-9X*]/g,'').toUpperCase().replace(/\*/g,'X');
                var mask2 = person.cpf.replace(/[^0-9X*]/g,'').toUpperCase().replace(/\*/g,'X');
                match = (mask1 === mask2);
            }
            
            text += '📌 PESSOA #' + (i + 1) + (match ? ' ✅ MATCH!' : '') + '\n';
            text += '   ├─ NOME: ' + person.name + '\n';
            if (person.cpf) text += '   ├─ CPF: ' + person.cpf + '\n';
            if (person.age) text += '   ├─ IDADE: ' + person.age + '\n';
            if (person.state) text += '   ├─ UF: ' + person.state + '\n';
            if (person.link) text += '   ├─ LINK: ' + person.link + '\n';
            
            if (person.companies.length) {
                text += '   └─ EMPRESAS:\n';
                for (var j = 0; j < person.companies.length; j++) {
                    var company = person.companies[j];
                    var prefix = (j === person.companies.length - 1) ? '      └─' : '      ├─';
                    var msg = prefix + ' ' + company.name + (company.legal && company.legal !== company.name ? ' (' + company.legal + ')' : '');
                    text += '      ' + msg + '\n';
                    if (company.cnpj) text += '         └─ CNPJ: ' + company.cnpj + '\n';
                    if (company.state) text += '            └─ UF: ' + company.state + '\n';
                }
            } else {
                text += '   └─ EMPRESAS: NENHUMA\n';
            }
            text += '\n';
        }
        
        text += separator + '  FIM DO RELATÓRIO\n' + separator;
        
        var blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
        var url = URL.createObjectURL(blob);
        var link = document.createElement('a');
        link.href = url;
        link.download = 'xrav_relatorio_' + new Date().toISOString().slice(0,10) + '.txt';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        log_message('EXPORTADO COM SUCESSO', '#51cf66', '<i class="fas fa-file-export"></i>');
    }
    
    // ============================================================
    // FUNÇÕES PRINCIPAIS DE CONTROLE
    // ============================================================
    
    function init_scan() {
        if (X.running || X.processing) return;
        
        var name_input = document.getElementById('xrav-name');
        var cpf_input = document.getElementById('xrav-cpf');
        var delay_input = document.getElementById('xrav-delay');
        
        var name = name_input.value.trim();
        var mask = cpf_input.value.trim();
        var delay = parseInt(delay_input.value) || 3000;
        
        if (!name) {
            alert('Digite o nome!');
            name_input.focus();
            return;
        }
        if (!mask) {
            alert('Digite a máscara CPF! Ex: ***.123.123-**');
            cpf_input.focus();
            return;
        }
        if (delay < 1000) {
            alert('Delay mínimo: 1000ms');
            delay_input.focus();
            return;
        }
        
        X.name = name;
        X.cpfMask = mask;
        X.delay = delay;
        X.stop = false;
        X.running = true;
        X.people = [];
        X.results = [];
        X.stats = { total: 0, withCPF: 0, withoutCPF: 0, companies: 0, states: {}, ages: [] };
        
        var button = document.getElementById('xrav-btn');
        if (button) {
            button.innerHTML = '<i class="fas fa-stop"></i> PARAR';
            button.style.background = '#ff6b6b';
        }
        
        update_status('SCANEANDO...', 'running');
        clear_log();
        
        var results = detect_results();
        if (!results.length) {
            log_message('NENHUM ALVO ENCONTRADO', '#ff4444', '<i class="fas fa-times"></i>');
            log_message('DICA: Faça uma busca no Jusbrasil primeiro', '#ffd43b');
            X.running = false;
            if (button) {
                button.innerHTML = '<i class="fas fa-play"></i> INICIAR';
                button.style.background = '#20c997';
            }
            update_status('PRONTO');
            return;
        }
        
        log_message('ALVOS ENCONTRADOS: ' + results.length, '#51cf66', '<i class="fas fa-check"></i>');
        process_results(results, mask, delay);
    }
    
    function stop_scan() {
        if (X.running || X.processing) {
            X.stop = true;
            log_message('ABORTANDO SCAN...', '#ff4444', '<i class="fas fa-stop"></i>');
        }
    }
    
    function toggle_scan() {
        if (X.running || X.processing) {
            stop_scan();
        } else {
            init_scan();
        }
    }
    
    // ============================================================
    // CRIAÇÃO DA INTERFACE DE USUÁRIO
    // ============================================================
    
    function create_ui() {
        var old_ui = document.getElementById('xrav-ui');
        if (old_ui) old_ui.remove();
        
        var container = document.createElement('div');
        container.id = 'xrav-ui';
        container.style.cssText = [
            'position:fixed', 'top:20px', 'right:20px', 'width:540px', 'max-height:95vh',
            'background:linear-gradient(160deg, #0d0d0d, #141414, #0a0a0a)',
            'color:#e9ecef', 'border-radius:12px',
            'box-shadow:0 8px 32px rgba(0,0,0,0.8), 0 0 40px rgba(0,255,136,0.03)',
            'z-index:999999',
            'font-family:"Segoe UI", system-ui, -apple-system, sans-serif', 'font-size:13px',
            'border:1px solid rgba(255,255,255,0.06)',
            'display:flex', 'flex-direction:column', 'overflow:hidden',
            'cursor:move', 'user-select:none',
            'backdrop-filter:blur(10px)'
        ].join(';');
        
        var header = document.createElement('div');
        header.style.cssText = 'padding:16px 20px;background:rgba(0,0,0,0.3);border-bottom:1px solid rgba(255,255,255,0.05);display:flex;justify-content:space-between;align-items:center;cursor:move;flex-shrink:0;';
        
        var title = document.createElement('div');
        title.style.cssText = 'font-weight:700;font-size:16px;color:#e9ecef;display:flex;align-items:center;gap:10px;';
        title.innerHTML = '<i class="fas fa-search" style="color:#20c997;font-size:18px;"></i> XRAV JUSBR';
        
        var close_button = document.createElement('button');
        close_button.innerHTML = '<i class="fas fa-times"></i>';
        close_button.style.cssText = 'background:transparent;border:1px solid rgba(255,255,255,0.05);color:rgba(255,255,255,0.3);font-size:14px;cursor:pointer;padding:4px 10px;border-radius:6px;transition:all 0.2s;';
        close_button.onmouseover = function() {
            this.style.borderColor = 'rgba(255,255,255,0.2)';
            this.style.color = '#ffffff';
        };
        close_button.onmouseout = function() {
            this.style.borderColor = 'rgba(255,255,255,0.05)';
            this.style.color = 'rgba(255,255,255,0.3)';
        };
        close_button.onclick = function() {
            document.getElementById('xrav-ui').style.display = 'none';
        };
        
        header.appendChild(title);
        header.appendChild(close_button);
        container.appendChild(header);
        
        var body = document.createElement('div');
        body.style.cssText = 'padding:16px 20px;overflow-y:auto;flex:1;min-height:0;';
        
        // Status
        var status_div = document.createElement('div');
        status_div.id = 'xrav-status';
        status_div.style.cssText = 'background:rgba(32,201,153,0.05);border:1px solid rgba(32,201,153,0.1);border-radius:8px;padding:10px 14px;margin-bottom:16px;font-size:13px;font-weight:500;display:flex;align-items:center;gap:8px;color:#20c997;';
        status_div.innerHTML = '<i class="fas fa-circle" style="color:#20c997;font-size:8px;"></i> PRONTO';
        body.appendChild(status_div);
        
        // Nome
        var name_label = document.createElement('label');
        name_label.innerHTML = '<i class="fas fa-user" style="margin-right:8px;color:#4dabf7;"></i> NOME DO ALVO:';
        name_label.style.cssText = 'display:block;margin-bottom:4px;font-weight:600;font-size:11px;color:#adb5bd;letter-spacing:0.3px;text-transform:uppercase;';
        body.appendChild(name_label);
        
        var name_input = document.createElement('input');
        name_input.id = 'xrav-name';
        name_input.type = 'text';
        name_input.placeholder = 'Detectando nome automaticamente...';
        name_input.style.cssText = 'width:100%;padding:10px 14px;border:1px solid rgba(255,255,255,0.06);border-radius:8px;background:rgba(0,0,0,0.4);color:#e9ecef;font-size:14px;font-family:"Segoe UI", system-ui, sans-serif;box-sizing:border-box;outline:none;transition:all 0.3s;';
        name_input.onfocus = function() {
            this.style.borderColor = 'rgba(77,171,247,0.3)';
            this.style.background = 'rgba(0,0,0,0.6)';
            this.style.boxShadow = '0 0 20px rgba(77,171,247,0.05)';
        };
        name_input.onblur = function() {
            this.style.borderColor = 'rgba(255,255,255,0.06)';
            this.style.background = 'rgba(0,0,0,0.4)';
            this.style.boxShadow = 'none';
        };
        body.appendChild(name_input);
        body.appendChild(document.createElement('br'));
        body.appendChild(document.createElement('br'));
        
        // CPF
        var cpf_label = document.createElement('label');
        cpf_label.innerHTML = '<i class="fas fa-id-card" style="margin-right:8px;color:#ffd43b;"></i> MÁSCARA CPF:';
        cpf_label.style.cssText = 'display:block;margin-bottom:4px;font-weight:600;font-size:11px;color:#adb5bd;letter-spacing:0.3px;text-transform:uppercase;';
        body.appendChild(cpf_label);
        
        var cpf_input = document.createElement('input');
        cpf_input.id = 'xrav-cpf';
        cpf_input.type = 'text';
        cpf_input.placeholder = 'Ex: ***.123.123-** (preencher manualmente)';
        cpf_input.style.cssText = 'width:100%;padding:10px 14px;border:1px solid rgba(255,255,255,0.06);border-radius:8px;background:rgba(0,0,0,0.4);color:#e9ecef;font-size:14px;font-family:"Segoe UI", system-ui, sans-serif;box-sizing:border-box;outline:none;transition:all 0.3s;';
        cpf_input.onfocus = function() {
            this.style.borderColor = 'rgba(255,212,59,0.3)';
            this.style.background = 'rgba(0,0,0,0.6)';
            this.style.boxShadow = '0 0 20px rgba(255,212,59,0.05)';
        };
        cpf_input.onblur = function() {
            this.style.borderColor = 'rgba(255,255,255,0.06)';
            this.style.background = 'rgba(0,0,0,0.4)';
            this.style.boxShadow = 'none';
        };
        body.appendChild(cpf_input);
        body.appendChild(document.createElement('br'));
        body.appendChild(document.createElement('br'));
        
        // Configurações
        var config_container = document.createElement('div');
        config_container.style.cssText = 'display:flex;gap:12px;';
        
        var delay_group = document.createElement('div');
        delay_group.style.cssText = 'flex:1;';
        var delay_label = document.createElement('label');
        delay_label.innerHTML = '<i class="fas fa-clock" style="margin-right:4px;color:#868e96;"></i> DELAY (ms):';
        delay_label.style.cssText = 'display:block;margin-bottom:4px;font-weight:600;font-size:10px;color:#868e96;letter-spacing:0.3px;text-transform:uppercase;';
        delay_group.appendChild(delay_label);
        
        var delay_input = document.createElement('input');
        delay_input.id = 'xrav-delay';
        delay_input.type = 'number';
        delay_input.value = '3000';
        delay_input.min = '1000';
        delay_input.max = '10000';
        delay_input.style.cssText = 'width:100%;padding:8px 12px;border:1px solid rgba(255,255,255,0.06);border-radius:8px;background:rgba(0,0,0,0.4);color:#e9ecef;font-size:13px;font-family:"Segoe UI", system-ui, sans-serif;box-sizing:border-box;outline:none;transition:all 0.3s;';
        delay_input.onfocus = function() {
            this.style.borderColor = 'rgba(255,255,255,0.2)';
            this.style.background = 'rgba(0,0,0,0.6)';
        };
        delay_input.onblur = function() {
            this.style.borderColor = 'rgba(255,255,255,0.06)';
            this.style.background = 'rgba(0,0,0,0.4)';
        };
        delay_group.appendChild(delay_input);
        config_container.appendChild(delay_group);
        
        var info_group = document.createElement('div');
        info_group.style.cssText = 'flex:1;display:flex;align-items:center;justify-content:center;flex-direction:column;background:rgba(32,201,153,0.03);border-radius:8px;border:1px solid rgba(32,201,153,0.05);padding:4px;';
        var info_text = document.createElement('div');
        info_text.style.cssText = 'font-size:10px;color:#868e96;text-align:center;letter-spacing:0.3px;';
        info_text.innerHTML = '<i class="fas fa-robot" style="font-size:20px;display:block;margin-bottom:2px;color:#20c997;"></i> DETECÇÃO AUTOMÁTICA';
        info_group.appendChild(info_text);
        config_container.appendChild(info_group);
        body.appendChild(config_container);
        body.appendChild(document.createElement('br'));
        
        // Botões
        var button_container = document.createElement('div');
        button_container.style.cssText = 'display:flex;gap:6px;flex-wrap:wrap;';
        
        var main_button = document.createElement('button');
        main_button.id = 'xrav-btn';
        main_button.innerHTML = '<i class="fas fa-play"></i> INICIAR';
        main_button.style.cssText = 'flex:2;padding:12px 16px;background:#20c997;border:none;border-radius:8px;color:#000;font-weight:700;font-size:13px;font-family:"Segoe UI", system-ui, sans-serif;cursor:pointer;transition:all 0.3s;display:flex;align-items:center;justify-content:center;gap:8px;';
        main_button.onmouseover = function() {
            this.style.transform = 'scale(1.02)';
            this.style.boxShadow = '0 4px 20px rgba(32,201,153,0.3)';
        };
        main_button.onmouseout = function() {
            this.style.transform = 'scale(1)';
            this.style.boxShadow = 'none';
        };
        main_button.onclick = toggle_scan;
        button_container.appendChild(main_button);
        
        var export_button = document.createElement('button');
        export_button.innerHTML = '<i class="fas fa-file-export"></i> EXPORTAR';
        export_button.style.cssText = 'flex:1;padding:12px 16px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:8px;color:#e9ecef;font-weight:600;font-size:12px;font-family:"Segoe UI", system-ui, sans-serif;cursor:pointer;transition:all 0.3s;display:flex;align-items:center;justify-content:center;gap:8px;';
        export_button.onmouseover = function() {
            this.style.background = 'rgba(255,255,255,0.06)';
            this.style.borderColor = 'rgba(255,255,255,0.12)';
        };
        export_button.onmouseout = function() {
            this.style.background = 'rgba(255,255,255,0.03)';
            this.style.borderColor = 'rgba(255,255,255,0.06)';
        };
        export_button.onclick = export_txt;
        button_container.appendChild(export_button);
        
        var clear_button = document.createElement('button');
        clear_button.innerHTML = '<i class="fas fa-trash-alt"></i> LIMPAR';
        clear_button.style.cssText = 'flex:1;padding:12px 16px;background:rgba(255,107,107,0.05);border:1px solid rgba(255,107,107,0.06);border-radius:8px;color:#ff6b6b;font-weight:600;font-size:12px;font-family:"Segoe UI", system-ui, sans-serif;cursor:pointer;transition:all 0.3s;display:flex;align-items:center;justify-content:center;gap:8px;';
        clear_button.onmouseover = function() {
            this.style.background = 'rgba(255,107,107,0.1)';
            this.style.borderColor = 'rgba(255,107,107,0.15)';
        };
        clear_button.onmouseout = function() {
            this.style.background = 'rgba(255,107,107,0.05)';
            this.style.borderColor = 'rgba(255,107,107,0.06)';
        };
        clear_button.onclick = function() {
            clear_log();
            X.people = [];
            X.results = [];
            update_status('PRONTO');
        };
        button_container.appendChild(clear_button);
        body.appendChild(button_container);
        body.appendChild(document.createElement('br'));
        
        // Log
        var log_header = document.createElement('div');
        log_header.style.cssText = 'display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;';
        var log_label = document.createElement('div');
        log_label.innerHTML = '<i class="fas fa-terminal" style="margin-right:6px;color:#868e96;"></i> LOG:';
        log_label.style.cssText = 'font-weight:600;font-size:11px;color:#adb5bd;letter-spacing:0.3px;text-transform:uppercase;';
        log_header.appendChild(log_label);
        
        var log_count = document.createElement('span');
        log_count.id = 'xrav-log-count';
        log_count.textContent = '0 linhas';
        log_count.style.cssText = 'font-size:10px;color:#868e96;';
        log_header.appendChild(log_count);
        body.appendChild(log_header);
        
        var log_element = document.createElement('div');
        log_element.id = 'xrav-log';
        log_element.style.cssText = 'background:rgba(0,0,0,0.5);border-radius:8px;padding:10px 14px;max-height:180px;overflow-y:auto;font-family:"Consolas", "Courier New", monospace;font-size:11px;line-height:1.6;border:1px solid rgba(255,255,255,0.04);white-space:pre-wrap;word-wrap:break-word;color:#adb5bd;';
        log_element.textContent = '> AGUARDANDO COMANDO...\n';
        body.appendChild(log_element);
        container.appendChild(body);
        
        // Footer
        var footer = document.createElement('div');
        footer.style.cssText = 'padding:8px 20px;background:rgba(0,0,0,0.2);border-top:1px solid rgba(255,255,255,0.03);font-size:9px;color:#868e96;text-align:center;cursor:default;flex-shrink:0;display:flex;justify-content:center;align-items:center;gap:16px;font-family:"Segoe UI", system-ui, sans-serif;letter-spacing:0.3px;';
        footer.innerHTML = '<span><i class="fas fa-search" style="color:#20c997;margin-right:4px;"></i> XRAV</span><span><i class="fas fa-arrows-alt" style="margin-right:4px;"></i> ARRASTE</span><span><i class="fas fa-shield-alt" style="color:#4dabf7;margin-right:4px;"></i> SEGURO</span>';
        container.appendChild(footer);
        
        // Drag functionality
        var is_dragging = false, offset_x, offset_y;
        container.addEventListener('mousedown', function(e) {
            if (e.target.closest('button') || e.target.closest('input')) return;
            is_dragging = true;
            var rect = container.getBoundingClientRect();
            offset_x = e.clientX - rect.left;
            offset_y = e.clientY - rect.top;
            container.style.cursor = 'grabbing';
            container.style.transition = 'none';
        });
        
        document.addEventListener('mousemove', function(e) {
            if (!is_dragging) return;
            var x = e.clientX - offset_x;
            var y = e.clientY - offset_y;
            x = Math.max(0, Math.min(window.innerWidth - container.offsetWidth, x));
            y = Math.max(0, Math.min(window.innerHeight - container.offsetHeight, y));
            container.style.left = x + 'px';
            container.style.top = y + 'px';
            container.style.right = 'auto';
        });
        
        document.addEventListener('mouseup', function() {
            if (is_dragging) {
                is_dragging = false;
                container.style.cursor = 'move';
                container.style.transition = 'all 0.3s ease';
            }
        });
        
        document.body.appendChild(container);
        setTimeout(auto_detect_name, 500);
    }
    
    // ============================================================
    // INICIALIZAÇÃO
    // ============================================================
    
    console.log('XRAV JUSBR CARREGANDO...');
    if (document.getElementById('xrav-ui')) {
        document.getElementById('xrav-ui').remove();
    }
    create_ui();
    console.log('XRAV JUSBR PRONTO');
    console.log('REALIZE A BUSCA NO JUSBRASIL PRIMEIRO');
})();
'''
    
    def generate_script(self) -> str:
        """
        Gera o script JavaScript completo.
        
        Returns:
            str: Script JavaScript completo para execução no navegador
        """
        return self._script_template


class UIBuilder:
    """Constrói a interface de usuário no terminal."""
    
    def __init__(self) -> None:
        """Inicializa o construtor de interface."""
        self._colors = TerminalColors()
    
    def _print_header(self) -> None:
        """Exibe o cabeçalho do programa."""
        print(f"""
{self._colors.GREEN}╔══════════════════════════════════════════════════════════════╗
║                    XRAV JUSBR                                ║
╚══════════════════════════════════════════════════════════════╝{self._colors.RESET}
""")
    
    def _print_features(self) -> None:
        """Exibe as funcionalidades do programa."""
        print(f"""{self._colors.WHITE}🔍 Detecta automaticamente o nome da pessoa pesquisada
🎯 Busca por CPFs específicos usando máscaras personalizadas
📊 Gera relatórios com todas as informações relevantes extraídas
🏢 Identifica empresas e vínculos societários
""")
    
    def _print_instructions(self) -> None:
        """Exibe as instruções de uso do programa."""
        print(f"""
{self._colors.GREEN}╔══════════════════════════════════════════════════════════════╗
║                    INSTRUÇÕES DE USO                         ║
╚══════════════════════════════════════════════════════════════╝{self._colors.RESET}

{self._colors.WHITE}1. Acesse https://www.jusbrasil.com.br
2. Faça a busca da pessoa desejada
3. Pressione F12 → Abra a aba Console
4. Cole TODO o script e pressione ENTER
5. A interface aparecerá e detectará automaticamente
6. Preencha a máscara CPF e clique em INICIAR
""")
    
    def _print_cpf_examples(self) -> None:
        """Exibe exemplos de máscaras CPF."""
        print(f"""
{self._colors.MAGENTA}╔══════════════════════════════════════════════════════════════╗
║                    EXEMPLO DE MÁSCARA CPF                    ║
╚══════════════════════════════════════════════════════════════╝{self._colors.RESET}

{self._colors.WHITE}📌 ***.123.123-** → Busca CPFs com os dígitos centrais
📌 123.123.123-** → Busca CPFs com os primeiros 9 dígitos fixos
📌 Use * (asterisco) para representar dígitos desconhecidos.
""")
    
    def _print_warnings(self) -> None:
        """Exibe avisos importantes sobre o uso do programa."""
        print(f"""
{self._colors.RED}╔══════════════════════════════════════════════════════════════╗
║                    ATENÇÃO                                   ║
╚══════════════════════════════════════════════════════════════╝{self._colors.RESET}

{self._colors.YELLOW}⚠️  Respeite as leis e use apenas para fins legítimos
⚠️  O delay entre requisições evita sobrecarga no servidor
⚠️  Recomendado: delay mínimo de 1000ms entre requisições
""")
    
    def display_welcome(self) -> None:
        """Exibe a mensagem de boas-vindas completa."""
        self._print_header()
        self._print_features()
        self._print_instructions()
        self._print_cpf_examples()
        self._print_warnings()
    
    def display_success(self, filename: str, script_length: int) -> None:
        """
        Exibe mensagem de sucesso após geração do script.
        
        Args:
            filename: Nome do arquivo gerado
            script_length: Tamanho do script em caracteres
        """
        print(f"""
{self._colors.GREEN}✅ Script gerado com sucesso!{self._colors.RESET}
{self._colors.WHITE}📁 Arquivo: {self._colors.GREEN}{filename}{self._colors.RESET}
{self._colors.WHITE}📊 Tamanho: {self._colors.YELLOW}{script_length:,}{self._colors.RESET}{self._colors.WHITE} caracteres{self._colors.RESET}

┌────────────────────────────────────────────────────┐
│ PRÓXIMOS PASSOS:                                   │
│ 1. Abra o arquivo gerado no editor de texto        │
│ 2. Selecione TODO o conteúdo (Ctrl+A)              │
│ 3. Copie (Ctrl+C)                                  │
│ 4. Cole no Console do navegador (Ctrl+V)           │
└────────────────────────────────────────────────────┘

{self._colors.YELLOW}💡 Dica: Mantenha a aba do Jusbrasil ativa durante a execução
{self._colors.WHITE}
""")


def generate_output_filename(output_file: Optional[str] = None) -> str:
    """
    Gera o nome do arquivo de saída.
    
    Args:
        output_file: Nome do arquivo especificado pelo usuário
        
    Returns:
        str: Nome do arquivo formatado
    """
    if output_file:
        filename = output_file
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'devtools-xrav-jusbr-{timestamp}.txt'
    
    if not filename.endswith('.txt'):
        filename += '.txt'
    
    return filename


def save_script_to_file(script_content: str, filename: str) -> None:
    """
    Salva o script em um arquivo.
    
    Args:
        script_content: Conteúdo do script a ser salvo
        filename: Nome do arquivo de destino
        
    Raises:
        IOError: Se ocorrer erro ao salvar o arquivo
    """
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(script_content)
        logger.info(f"Script salvo com sucesso em: {filename}")
    except IOError as error:
        logger.error(f"Erro ao salvar arquivo: {error}")
        raise


def parse_arguments() -> argparse.Namespace:
    """
    Analisa os argumentos da linha de comando.
    
    Returns:
        argparse.Namespace: Argumentos parseados
    """
    parser = argparse.ArgumentParser(
        prog=os.path.basename(sys.argv[0]),
        description="Gera script da interface"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Salva o script em um arquivo específico"
    )
    return parser.parse_args()


def main() -> None:
    """
    Função principal do programa.
    
    Coordena a execução do programa, desde o parsing dos argumentos
    até a geração e salvamento do script.
    """
    try:
        args = parse_arguments()
        
        ui_builder = UIBuilder()
        ui_builder.display_welcome()
        
        script_generator = ScriptGenerator()
        script_content = script_generator.generate_script()
        
        filename = generate_output_filename(args.output)
        save_script_to_file(script_content, filename)
        
        ui_builder.display_success(filename, len(script_content))
        
    except KeyboardInterrupt:
        logger.info("Programa interrompido pelo usuário")
        print(f"\n{TerminalColors.YELLOW}⚠️  Operação cancelada pelo usuário{TerminalColors.RESET}")
    except Exception as error:
        logger.error(f"Erro inesperado: {error}", exc_info=True)
        print(f"\n{TerminalColors.RED}❌ Erro: {error}{TerminalColors.RESET}")
        raise


if __name__ == "__main__":
    main()
