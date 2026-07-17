#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from datetime import datetime

class Cores:
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    AZUL = '\033[94m'
    MAGENTA = '\033[95m'
    CIANO = '\033[96m'
    BRANCO = '\033[97m'
    VERMELHO = '\033[91m'
    RESET = '\033[0m'

class GeradorDevToolsUI:
    def __init__(self):
        pass
    
    def gerar_script_ui(self) -> str:
        return r'''
(function() {
    'use strict';
    
    (function(){
        var l=document.createElement('link');
        l.rel='stylesheet';
        l.href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';
        l.integrity='sha512-iecdLmaskl7CVkqkXNQ/ZH/XLlvWZOJyj7Yy7tcenmpD1ypASozpmT/E0iPtmFIB46ZmdtAc9eNBvH0H/ZpiBw==';
        l.crossOrigin='anonymous';
        document.head.appendChild(l);
    })();
    
    var X = window.XRAV || {};
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
    X.stats = { total: 0, withCPF: 0, withoutCPF: 0, companies: 0, states: {}, ages: [] };
    
    function detectNameFromPage() {
        var name = '';
        var h1Elements = document.querySelectorAll('h1');
        
        for (var i = 0; i < h1Elements.length; i++) {
            var h1 = h1Elements[i];
            var h1Text = h1.textContent || '';
            
            if (h1Text.includes('Consulta processual')) {
                var strongs = h1.querySelectorAll('strong');
                for (var j = 0; j < strongs.length; j++) {
                    var strongText = strongs[j].textContent.trim();
                    if (strongText && strongText.length > 3) {
                        name = strongText;
                        return name;
                    }
                }
                
                var match = h1Text.match(/sobre\s+([^<]+)/);
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
        
        var urlParams = new URLSearchParams(window.location.search);
        var qParam = urlParams.get('q');
        if (qParam) {
            name = decodeURIComponent(qParam).replace(/\+/g, ' ');
            if (name.length > 3) return name;
        }
        
        var selectors = ['h1', 'h2', 'h3', '[data-testid="header-name"]'];
        for (var s = 0; s < selectors.length; s++) {
            var elements = document.querySelectorAll(selectors[s]);
            for (var e = 0; e < elements.length; e++) {
                var text = elements[e].textContent.trim();
                var words = text.split(/\s+/);
                if (words.length >= 2 && text.length < 100 && text.length > 5) {
                    var genericTerms = ['resultados', 'busca', 'consulta', 'processual', 'sobre'];
                    var isGeneric = false;
                    for (var g = 0; g < genericTerms.length; g++) {
                        if (text.toLowerCase().includes(genericTerms[g])) {
                            isGeneric = true;
                            break;
                        }
                    }
                    if (!isGeneric) return text;
                }
            }
        }
        
        return '';
    }
    
    function autoDetectName() {
        var nameInput = document.getElementById('xrav-name');
        if (!nameInput) return;
        
        var detectedName = detectNameFromPage();
        if (detectedName) {
            nameInput.value = detectedName;
            nameInput.style.borderColor = '#00ff88';
            nameInput.style.boxShadow = '0 0 20px rgba(0,255,136,0.2)';
            nameInput.style.background = 'rgba(0,255,136,0.05)';
            X.name = detectedName;
            
            var logEl = document.getElementById('xrav-log');
            if (logEl) {
                var line = document.createElement('div');
                line.style.cssText = 'padding:4px 0;border-bottom:1px solid rgba(0,255,136,0.05);font-size:12px;font-family:"Courier New",monospace;';
                line.innerHTML = '<span style="color:#00ff88;">NOME DETECTADO: </span><span style="color:#ffffff;font-weight:bold;">' + detectedName + '</span>';
                logEl.appendChild(line);
                logEl.scrollTop = logEl.scrollHeight;
            }
        } else {
            nameInput.placeholder = 'Digite o nome (detecção falhou)';
            nameInput.style.borderColor = 'rgba(255,68,68,0.3)';
            nameInput.style.background = 'rgba(255,68,68,0.05)';
            
            var logEl = document.getElementById('xrav-log');
            if (logEl) {
                var line = document.createElement('div');
                line.style.cssText = 'padding:4px 0;border-bottom:1px solid rgba(255,68,68,0.05);font-size:12px;font-family:"Courier New",monospace;';
                line.innerHTML = '<span style="color:#ff4444;">NÃO DETECTADO - Informe manualmente</span>';
                logEl.appendChild(line);
                logEl.scrollTop = logEl.scrollHeight;
            }
        }
    }
    
    function validaCPF(c) {
        if(c.length!==11||!/^\d{11}$/.test(c)) return false;
        if(/^(\d)\1{10}$/.test(c)) return false;
        var s=0;
        for(var i=0;i<9;i++) s+=parseInt(c.charAt(i))*(10-i);
        var r=s%11;
        var d1=r<2?0:11-r;
        if(parseInt(c.charAt(9))!==d1) return false;
        s=0;
        for(var i=0;i<10;i++) s+=parseInt(c.charAt(i))*(11-i);
        r=s%11;
        var d2=r<2?0:11-r;
        return parseInt(c.charAt(10))===d2;
    }
    
    function fmtCPF(c){
        return c.substring(0,3)+'.'+c.substring(3,6)+'.'+c.substring(6,9)+'-'+c.substring(9,11);
    }
    
    function sleep(m){
        return new Promise(function(r){ setTimeout(r,m); });
    }
    
    function fmtTime(ms){
        var s=Math.floor(ms/1000);
        var m=Math.floor(s/60);
        s=s%60;
        return m>0?m+'m '+s+'s':s+'s';
    }
    
    function genCPFs(mask, limit) {
        limit = limit || 100;
        var clean = mask.replace(/[^0-9X*]/g,'').toUpperCase().replace(/\*/g,'X');
        if (clean.length !== 11) {
            alert('Mascara invalida! Use: ***.123.123-**');
            return [];
        }
        var xPos = [];
        for(var i=0;i<clean.length;i++){
            if(clean[i]==='X') xPos.push(i);
        }
        if(xPos.length===0) return validaCPF(clean)?[clean]:[];
        var candidates = [];
        var digits = [];
        for(var i=0;i<11;i++){
            if(xPos.indexOf(i)!==-1){
                digits.push(i===0?[1,2,3,4,5,6,7,8,9]:[0,1,2,3,4,5,6,7,8,9]);
            } else {
                digits.push([parseInt(clean[i])]);
            }
        }
        function combine(idx, cur){
            if(idx===digits.length){
                var c=cur.join('');
                if(validaCPF(c)) candidates.push(c);
                return;
            }
            for(var i=0;i<digits[idx].length;i++){
                var n=cur.slice();
                n.push(digits[idx][i]);
                combine(idx+1,n);
            }
        }
        combine(0,[]);
        return candidates.length>limit ? candidates.slice(0,limit) : candidates;
    }
    
    function extractData(html) {
        var d = {};
        var m;
        
        if((m=html.match(/<h1[^>]*data-testid="header-name"[^>]*>(.*?)<\/h1>/))) {
            d.name = m[1].replace(/<[^>]+>/g,'').trim();
        }
        if(!d.name) {
            var h1Match = html.match(/<h1[^>]*>(.*?)<\/h1>/);
            if(h1Match) d.name = h1Match[1].replace(/<[^>]+>/g,'').trim();
        }
        
        if((m=html.match(/CPF\s*<!--\s*-->\s*(\*{3}\.\d{3}\.\d{3}-\*{2})/))) d.cpf = m[1];
        if(!d.cpf) {
            var cpfPatterns = [
                /\b(\d{3}\.\d{3}\.\d{3}-\d{2})\b/,
                /\b(\*{3}\.\d{3}\.\d{3}-\*{2})\b/,
                /CPF[:\s]+([\d*.]{3,})/
            ];
            for(var p=0; p<cpfPatterns.length; p++) {
                if((m=html.match(cpfPatterns[p]))) {
                    d.cpf = m[1];
                    break;
                }
            }
        }
        
        var agePatterns = [
            /(\d+)\s*anos?/i,
            /idade[:\s]+(\d+)/i,
            /<span[^>]*>(\d+)\s*anos?/i
        ];
        for(var a=0; a<agePatterns.length; a++) {
            if((m=html.match(agePatterns[a]))) {
                d.age = m[1];
                break;
            }
        }
        
        var statePatterns = [
            /([A-Z]{2})\s*[•●]/,
            /[•●]\s*([A-Z]{2})/,
            /estado[:\s]+([A-Z]{2})/i,
            /uf[:\s]+([A-Z]{2})/i
        ];
        for(var s=0; s<statePatterns.length; s++) {
            if((m=html.match(statePatterns[s]))) {
                d.state = m[1];
                break;
            }
        }
        
        var companies = [];
        var companyPatterns = [
            /entity-summary[^>]*>(.*?)<\/div>\s*<\/div>\s*<\/div>/gs,
            /(?:empresa|company)[^>]*>(.*?)<\/div>/gi,
            /card[^>]*>(.*?)<\/div>/gi
        ];
        
        var cards = [];
        for(var i=0; i<companyPatterns.length; i++) {
            var matches = html.match(companyPatterns[i]);
            if(matches && matches.length > 0) {
                cards = matches;
                break;
            }
        }
        
        if(cards && cards.length > 0) {
            for(var i=0; i<Math.min(cards.length, 20); i++) {
                var card = cards[i];
                var emp = {};
                
                var nm = card.match(/>([^<]{3,50})<\/[a-z]/);
                if(nm) emp.name = nm[1].trim();
                
                var cnpjMatch = card.match(/\b(\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2})\b/);
                if(cnpjMatch) emp.cnpj = cnpjMatch[1];
                
                var stMatch = card.match(/\b([A-Z]{2})\b/);
                if(stMatch && stMatch[1].length === 2) emp.state = stMatch[1];
                
                if(emp.name && emp.name.length > 2) companies.push(emp);
            }
        }
        d.companies = companies;
        return d;
    }
    
    function log(msg, color, icon) {
        var el = document.getElementById('xrav-log');
        var cnt = document.getElementById('xrav-log-count');
        if(!el) return;
        var line = document.createElement('div');
        line.style.cssText = 'padding:4px 0;border-bottom:1px solid rgba(0,255,136,0.03);font-size:12px;font-family:"Courier New",monospace;line-height:1.4;';
        if(icon){
            var s=document.createElement('span');
            s.innerHTML=icon;
            s.style.cssText='margin-right:8px;display:inline-block;width:18px;text-align:center;';
            line.appendChild(s);
        }
        var t=document.createElement('span');
        if(color) t.style.color=color;
        t.textContent=msg;
        line.appendChild(t);
        el.appendChild(line);
        el.scrollTop=el.scrollHeight;
        if(cnt) cnt.textContent=el.children.length+' linhas';
        while(el.children.length>500) el.removeChild(el.firstChild);
    }
    
    function status(msg, type) {
        var el = document.getElementById('xrav-status');
        if(!el) return;
        var colors = { running:'#ff6b6b', success:'#51cf66', idle:'#20c997' };
        var bgColors = { running:'rgba(255,107,107,0.08)', success:'rgba(81,207,102,0.08)', idle:'rgba(32,201,153,0.05)' };
        var c = type==='running'?colors.running:type==='success'?colors.success:colors.idle;
        var bg = type==='running'?bgColors.running:type==='success'?bgColors.success:bgColors.idle;
        el.innerHTML = '<i class="fas fa-circle" style="color:'+c+';font-size:8px;margin-right:8px;"></i> ' + msg;
        el.style.borderColor = c;
        el.style.color = c;
        el.style.background = bg;
    }
    
    function clearLog(){
        var el=document.getElementById('xrav-log');
        var cnt=document.getElementById('xrav-log-count');
        if(el) el.innerHTML='';
        if(cnt) cnt.textContent='0 linhas';
        X.people=[];
        X.results=[];
        X.stats={total:0,withCPF:0,withoutCPF:0,companies:0,states:{},ages:[]};
    }
    
    function detectResults(){
        var r=[];
        var links = document.querySelectorAll('a[href*="/nome/"]');
        var processed = new Set();
        
        for(var i=0; i<links.length; i++) {
            var link = links[i];
            var href = link.getAttribute('href');
            
            if(!href || !href.includes('/cpf-')) continue;
            if(processed.has(href)) continue;
            processed.add(href);
            
            var fullLink = href;
            if(!href.startsWith('http')) fullLink = 'https://www.jusbrasil.com.br' + href;
            
            var name = '';
            var text = link.textContent.trim();
            if(text && text.length > 2 && text.length < 100) {
                name = text;
            } else {
                var parent = link.parentElement;
                var spans = parent ? parent.querySelectorAll('span') : [];
                for(var s=0; s<spans.length; s++) {
                    var spanText = spans[s].textContent.trim();
                    if(spanText && spanText.length > 2 && spanText.length < 80) {
                        name = spanText;
                        break;
                    }
                }
            }
            
            if(fullLink && name) {
                r.push({
                    link: fullLink,
                    name: name || 'N/I',
                    age: '',
                    state: '',
                    element: link
                });
            }
        }
        
        if(r.length === 0) {
            var cards = document.querySelectorAll('[class*="card"][class*="summary"]');
            for(var c=0; c<cards.length; c++) {
                var card = cards[c];
                var linkEl = card.querySelector('a[href*="/nome/"]');
                if(!linkEl) continue;
                
                var href = linkEl.getAttribute('href');
                if(!href || processed.has(href)) continue;
                processed.add(href);
                
                var fullLink = href;
                if(!href.startsWith('http')) fullLink = 'https://www.jusbrasil.com.br' + href;
                
                var name = linkEl.textContent.trim() || 'N/I';
                r.push({
                    link: fullLink,
                    name: name,
                    age: '',
                    state: '',
                    element: linkEl
                });
            }
        }
        
        return r;
    }
    
    async function fetchProfile(link){
        try{
            var resp=await fetch(link,{
                credentials:'include',
                headers:{
                    'Accept':'text/html',
                    'Accept-Language':'pt-BR,pt;q=0.9',
                    'Cache-Control':'no-cache',
                    'Pragma':'no-cache',
                    'User-Agent':navigator.userAgent
                }
            });
            if(!resp.ok) return null;
            var html=await resp.text();
            await sleep(500);
            return extractData(html);
        }catch(e){
            return null;
        }
    }
    
    async function processResults(results, cpfMask, delay){
        X.processing=true;
        var found=false, total=results.length, target=null;
        X.startTime=Date.now();
        X.stats={total:0,withCPF:0,withoutCPF:0,companies:0,states:{},ages:[]};
        
        log('═══════════════════════════════════════════════','#335533');
        log('INICIANDO SCAN','#00ff88','<i class="fas fa-search"></i>');
        log('ALVOS: '+total,'#00ff88','<i class="fas fa-bullseye"></i>');
        log('MASCARA CPF: '+cpfMask,'#ffd43b','<i class="fas fa-id-card"></i>');
        log('───────────────────────────────────────────────','#335533');
        
        for(var i=0;i<total;i++){
            if(X.stop){
                log('SCAN ABORTADO PELO USUARIO','#ff4444','<i class="fas fa-stop"></i>');
                break;
            }
            var res=results[i];
            var p='['+String(i+1).padStart(3,' ')+'/'+String(total).padStart(3,' ')+']';
            log(p+' SCAN: '+res.name,'#4dabf7','<i class="fas fa-user"></i>');
            
            var data=await fetchProfile(res.link);
            if(data){
                var person={
                    name:data.name||res.name,
                    link:res.link,
                    cpf:data.cpf,
                    age:data.age||res.age,
                    state:data.state||res.state,
                    companies:data.companies||[]
                };
                X.people.push(person);
                X.stats.total++;
                person.cpf?X.stats.withCPF++:X.stats.withoutCPF++;
                if(person.companies.length) X.stats.companies += person.companies.length;
                if(person.state){
                    if(!X.stats.states[person.state]) X.stats.states[person.state]=0;
                    X.stats.states[person.state]++;
                }
                if(person.age) X.stats.ages.push(person.age);
                
                var indent='     ';
                log(indent+'├─ NOME: '+person.name,'#ffffff');
                if(person.cpf){
                    log(indent+'├─ CPF: '+person.cpf,'#ffd43b');
                    var cleanMask=cpfMask.replace(/[^0-9X*]/g,'').toUpperCase().replace(/\*/g,'X');
                    var cleanCPF=person.cpf.replace(/[^0-9X*]/g,'').toUpperCase().replace(/\*/g,'X');
                    if(cleanMask===cleanCPF){
                        log(indent+'├─ MATCH ENCONTRADO!','#51cf66','<i class="fas fa-check"></i>');
                        found=true;
                        target=person;
                        X.results.push(person);
                    }
                }
                if(person.age) log(indent+'├─ IDADE: '+person.age,'#4dabf7');
                if(person.state) log(indent+'├─ UF: '+person.state,'#4dabf7');
                if(person.link) log(indent+'├─ LINK: '+person.link,'#868e96');
                
                if(person.companies.length){
                    log(indent+'└─ EMPRESAS:','#ff6b6b');
                    for(var j=0;j<person.companies.length;j++){
                        var c=person.companies[j];
                        var pre=(j===person.companies.length-1)?'   └─':'   ├─';
                        var msg=pre+' '+c.name+(c.legal&&c.legal!==c.name?' ('+c.legal+')':'');
                        log(indent+'   '+msg,'#ffd43b');
                        if(c.cnpj) log(indent+'      └─ CNPJ: '+c.cnpj,'#4dabf7');
                        if(c.state) log(indent+'         └─ UF: '+c.state,'#4dabf7');
                    }
                } else {
                    log(indent+'└─ EMPRESAS: NENHUMA','#868e96');
                }
                log('');
                if(found) break;
            } else {
                log('     FALHA NA REQUISIÇÃO','#ff4444','<i class="fas fa-times"></i>');
            }
            if(i<total-1 && !X.stop) await sleep(delay);
        }
        
        X.endTime=Date.now();
        var totalTime=X.endTime-X.startTime;
        X.stats.time=totalTime;
        X.stats.timeFmt=fmtTime(totalTime);
        
        log('═══════════════════════════════════════════════','#335533');
        log('ESTATISTICAS','#ffd43b','<i class="fas fa-chart-bar"></i>');
        log('───────────────────────────────────────────────','#335533');
        log('TEMPO: '+X.stats.timeFmt,'#ffffff');
        log('SCANEADOS: '+X.stats.total,'#ffffff');
        log('COM CPF: '+X.stats.withCPF,'#51cf66');
        log('SEM CPF: '+X.stats.withoutCPF,'#ff6b6b');
        log('EMPRESAS: '+X.stats.companies,'#ffd43b');
        
        var st=Object.keys(X.stats.states);
        if(st.length){
            log('UFs ENCONTRADAS:','#4dabf7');
            for(var k=0;k<st.length;k++){
                var s=st[k];
                var cnt=X.stats.states[s];
                var bar='';
                for(var b=0;b<Math.min(cnt,15);b++) bar+='█';
                log('  └─ '+s+': '+cnt+' '+bar,'#ffffff');
            }
        }
        if(X.stats.ages.length){
            var ageCnt={};
            for(var a=0;a<X.stats.ages.length;a++){
                var ag=X.stats.ages[a];
                if(!ageCnt[ag]) ageCnt[ag]=0;
                ageCnt[ag]++;
            }
            var ak=Object.keys(ageCnt);
            if(ak.length){
                log('IDADES:','#4dabf7');
                for(var a2=0;a2<ak.length;a2++){
                    var ag=ak[a2];
                    var cnt=ageCnt[ag];
                    var bar='';
                    for(var b2=0;b2<Math.min(cnt,15);b2++) bar+='█';
                    log('  └─ '+ag+' anos: '+cnt+' '+bar,'#ffffff');
                }
            }
        }
        log('═══════════════════════════════════════════════','#335533');
        
        if(found && target){
            log('','#51cf66');
            log('ALVO ENCONTRADO!','#51cf66','<i class="fas fa-trophy"></i>');
            log('═══════════════════════════════════════════════','#ffd43b');
            log('DADOS DO ALVO:','#ffd43b','<i class="fas fa-user"></i>');
            log('───────────────────────────────────────────────','#335533');
            log('  ├─ NOME: '+target.name,'#ffffff');
            if(target.cpf) log('  ├─ CPF: '+target.cpf,'#ffd43b');
            if(target.age) log('  ├─ IDADE: '+target.age,'#4dabf7');
            if(target.state) log('  ├─ UF: '+target.state,'#4dabf7');
            if(target.link) log('  ├─ LINK: '+target.link,'#868e96');
            if(target.companies.length){
                log('  └─ EMPRESAS:','#ff6b6b');
                for(var e=0;e<target.companies.length;e++){
                    var c=target.companies[e];
                    var pre=(e===target.companies.length-1)?'     └─':'     ├─';
                    var msg=pre+' '+c.name+(c.legal&&c.legal!==c.name?' ('+c.legal+')':'');
                    log('     '+msg,'#ffd43b');
                    if(c.cnpj) log('        └─ CNPJ: '+c.cnpj,'#4dabf7');
                    if(c.state) log('           └─ UF: '+c.state,'#4dabf7');
                }
            }
            log('═══════════════════════════════════════════════','#ffd43b');
            status('ALVO ENCONTRADO!','success');
        } else if(!X.stop) {
            log('');
            log('ALVO NÃO ENCONTRADO','#ff4444','<i class="fas fa-times"></i>');
        }
        
        X.processing=false;
        X.running=false;
        if(!found) status('PRONTO');
        var btn=document.getElementById('xrav-btn');
        if(btn){
            btn.innerHTML='<i class="fas fa-play"></i> INICIAR';
            btn.style.background='#20c997';
        }
    }
    
    function exportTXT(){
        if(!X.people.length){
            alert('Sem dados para exportar!');
            return;
        }
        var txt='';
        var sep='═══════════════════════════════════════════════════════════\n';
        var div='───────────────────────────────────────────────────────────\n';
        txt+=sep+'  XRAV JUSBR - RELATÓRIO DE INVESTIGAÇÃO\n'+sep;
        txt+='  DATA: '+new Date().toLocaleString()+'\n';
        txt+='  NOME: '+X.name+'\n';
        txt+='  MASCARA CPF: '+X.cpfMask+'\n';
        txt+='  SCANEADOS: '+X.people.length+'\n';
        if(X.stats.timeFmt) txt+='  TEMPO: '+X.stats.timeFmt+'\n';
        txt+=sep+'\n';
        txt+='📊 ESTATÍSTICAS\n'+div;
        txt+='  👤 SCANEADOS: '+X.stats.total+'\n';
        txt+='  🔢 COM CPF: '+X.stats.withCPF+'\n';
        txt+='  ❓ SEM CPF: '+X.stats.withoutCPF+'\n';
        txt+='  🏢 EMPRESAS: '+X.stats.companies+'\n';
        var st=Object.keys(X.stats.states);
        if(st.length){
            txt+='  📍 UFs:\n';
            for(var k=0;k<st.length;k++){
                txt+='     └─ '+st[k]+': '+X.stats.states[st[k]]+'\n';
            }
        }
        txt+='\n👤 PESSOAS ENCONTRADAS\n'+div;
        for(var i=0;i<X.people.length;i++){
            var p=X.people[i];
            var match=false;
            if(p.cpf){
                var m1=X.cpfMask.replace(/[^0-9X*]/g,'').toUpperCase().replace(/\*/g,'X');
                var m2=p.cpf.replace(/[^0-9X*]/g,'').toUpperCase().replace(/\*/g,'X');
                match=(m1===m2);
            }
            txt+='📌 PESSOA #'+(i+1)+(match?' ✅ MATCH!':'')+'\n';
            txt+='   ├─ NOME: '+p.name+'\n';
            if(p.cpf) txt+='   ├─ CPF: '+p.cpf+'\n';
            if(p.age) txt+='   ├─ IDADE: '+p.age+'\n';
            if(p.state) txt+='   ├─ UF: '+p.state+'\n';
            if(p.link) txt+='   ├─ LINK: '+p.link+'\n';
            if(p.companies.length){
                txt+='   └─ EMPRESAS:\n';
                for(var j=0;j<p.companies.length;j++){
                    var c=p.companies[j];
                    var pre=(j===p.companies.length-1)?'      └─':'      ├─';
                    var msg=pre+' '+c.name+(c.legal&&c.legal!==c.name?' ('+c.legal+')':'');
                    txt+='      '+msg+'\n';
                    if(c.cnpj) txt+='         └─ CNPJ: '+c.cnpj+'\n';
                    if(c.state) txt+='            └─ UF: '+c.state+'\n';
                }
            } else {
                txt+='   └─ EMPRESAS: NENHUMA\n';
            }
            txt+='\n';
        }
        txt+=sep+'  FIM DO RELATÓRIO\n'+sep;
        var blob=new Blob([txt],{type:'text/plain;charset=utf-8'});
        var url=URL.createObjectURL(blob);
        var a=document.createElement('a');
        a.href=url;
        a.download='xrav_relatorio_'+new Date().toISOString().slice(0,10)+'.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        log('EXPORTADO COM SUCESSO','#51cf66','<i class="fas fa-file-export"></i>');
    }
    
    function initScan(){
        if(X.running||X.processing) return;
        var n=document.getElementById('xrav-name');
        var c=document.getElementById('xrav-cpf');
        var d=document.getElementById('xrav-delay');
        var name=n.value.trim();
        var mask=c.value.trim();
        var delay=parseInt(d.value)||3000;
        if(!name){
            alert('Digite o nome!');
            n.focus();
            return;
        }
        if(!mask){
            alert('Digite a máscara CPF! Ex: ***.123.123-**');
            c.focus();
            return;
        }
        if(delay<1000){
            alert('Delay mínimo: 1000ms');
            d.focus();
            return;
        }
        X.name=name;
        X.cpfMask=mask;
        X.delay=delay;
        X.stop=false;
        X.running=true;
        X.people=[];
        X.results=[];
        X.stats={total:0,withCPF:0,withoutCPF:0,companies:0,states:{},ages:[]};
        var btn=document.getElementById('xrav-btn');
        if(btn){
            btn.innerHTML='<i class="fas fa-stop"></i> PARAR';
            btn.style.background='#ff6b6b';
        }
        status('SCANEANDO...','running');
        clearLog();
        var results=detectResults();
        if(!results.length){
            log('NENHUM ALVO ENCONTRADO','#ff4444','<i class="fas fa-times"></i>');
            log('DICA: Faça uma busca no Jusbrasil primeiro','#ffd43b');
            X.running=false;
            if(btn){
                btn.innerHTML='<i class="fas fa-play"></i> INICIAR';
                btn.style.background='#20c997';
            }
            status('PRONTO');
            return;
        }
        log('ALVOS ENCONTRADOS: '+results.length,'#51cf66','<i class="fas fa-check"></i>');
        processResults(results, mask, delay);
    }
    
    function killScan(){
        if(X.running||X.processing){
            X.stop=true;
            log('ABORTANDO SCAN...','#ff4444','<i class="fas fa-stop"></i>');
        }
    }
    
    function toggleScan(){
        X.running||X.processing?killScan():initScan();
    }
    
    function createUI(){
        var old=document.getElementById('xrav-ui');
        if(old) old.remove();
        
        var container=document.createElement('div');
        container.id='xrav-ui';
        container.style.cssText=[
            'position:fixed','top:20px','right:20px','width:540px','max-height:95vh',
            'background:linear-gradient(160deg, #0d0d0d, #141414, #0a0a0a)',
            'color:#e9ecef','border-radius:12px',
            'box-shadow:0 8px 32px rgba(0,0,0,0.8), 0 0 40px rgba(0,255,136,0.03)',
            'z-index:999999',
            'font-family:"Segoe UI", system-ui, -apple-system, sans-serif','font-size:13px',
            'border:1px solid rgba(255,255,255,0.06)',
            'display:flex','flex-direction:column','overflow:hidden',
            'cursor:move','user-select:none',
            'backdrop-filter:blur(10px)'
        ].join(';');
        
        var header=document.createElement('div');
        header.style.cssText='padding:16px 20px;background:rgba(0,0,0,0.3);border-bottom:1px solid rgba(255,255,255,0.05);display:flex;justify-content:space-between;align-items:center;cursor:move;flex-shrink:0;';
        var title=document.createElement('div');
        title.style.cssText='font-weight:700;font-size:16px;color:#e9ecef;display:flex;align-items:center;gap:10px;';
        title.innerHTML='<i class="fas fa-search" style="color:#20c997;font-size:18px;"></i> XRAV JUSBR';
        
        var close=document.createElement('button');
        close.innerHTML='<i class="fas fa-times"></i>';
        close.style.cssText='background:transparent;border:1px solid rgba(255,255,255,0.05);color:rgba(255,255,255,0.3);font-size:14px;cursor:pointer;padding:4px 10px;border-radius:6px;transition:all 0.2s;';
        close.onmouseover=function(){
            this.style.borderColor='rgba(255,255,255,0.2)';
            this.style.color='#ffffff';
        };
        close.onmouseout=function(){
            this.style.borderColor='rgba(255,255,255,0.05)';
            this.style.color='rgba(255,255,255,0.3)';
        };
        close.onclick=function(){
            document.getElementById('xrav-ui').style.display='none';
        };
        header.appendChild(title);
        header.appendChild(close);
        container.appendChild(header);
        
        var body=document.createElement('div');
        body.style.cssText='padding:16px 20px;overflow-y:auto;flex:1;min-height:0;';
        
        var statusDiv=document.createElement('div');
        statusDiv.id='xrav-status';
        statusDiv.style.cssText='background:rgba(32,201,153,0.05);border:1px solid rgba(32,201,153,0.1);border-radius:8px;padding:10px 14px;margin-bottom:16px;font-size:13px;font-weight:500;display:flex;align-items:center;gap:8px;color:#20c997;';
        statusDiv.innerHTML='<i class="fas fa-circle" style="color:#20c997;font-size:8px;"></i> PRONTO';
        body.appendChild(statusDiv);
        
        var nl=document.createElement('label');
        nl.innerHTML='<i class="fas fa-user" style="margin-right:8px;color:#4dabf7;"></i> NOME DO ALVO:';
        nl.style.cssText='display:block;margin-bottom:4px;font-weight:600;font-size:11px;color:#adb5bd;letter-spacing:0.3px;text-transform:uppercase;';
        body.appendChild(nl);
        var ni=document.createElement('input');
        ni.id='xrav-name';
        ni.type='text';
        ni.placeholder='Detectando nome automaticamente...';
        ni.style.cssText='width:100%;padding:10px 14px;border:1px solid rgba(255,255,255,0.06);border-radius:8px;background:rgba(0,0,0,0.4);color:#e9ecef;font-size:14px;font-family:"Segoe UI", system-ui, sans-serif;box-sizing:border-box;outline:none;transition:all 0.3s;';
        ni.onfocus=function(){
            this.style.borderColor='rgba(77,171,247,0.3)';
            this.style.background='rgba(0,0,0,0.6)';
            this.style.boxShadow='0 0 20px rgba(77,171,247,0.05)';
        };
        ni.onblur=function(){
            this.style.borderColor='rgba(255,255,255,0.06)';
            this.style.background='rgba(0,0,0,0.4)';
            this.style.boxShadow='none';
        };
        body.appendChild(ni);
        body.appendChild(document.createElement('br'));
        body.appendChild(document.createElement('br'));
        
        var cl=document.createElement('label');
        cl.innerHTML='<i class="fas fa-id-card" style="margin-right:8px;color:#ffd43b;"></i> MÁSCARA CPF:';
        cl.style.cssText='display:block;margin-bottom:4px;font-weight:600;font-size:11px;color:#adb5bd;letter-spacing:0.3px;text-transform:uppercase;';
        body.appendChild(cl);
        var ci=document.createElement('input');
        ci.id='xrav-cpf';
        ci.type='text';
        ci.placeholder='Ex: ***.123.123-** (preencher manualmente)';
        ci.style.cssText='width:100%;padding:10px 14px;border:1px solid rgba(255,255,255,0.06);border-radius:8px;background:rgba(0,0,0,0.4);color:#e9ecef;font-size:14px;font-family:"Segoe UI", system-ui, sans-serif;box-sizing:border-box;outline:none;transition:all 0.3s;';
        ci.onfocus=function(){
            this.style.borderColor='rgba(255,212,59,0.3)';
            this.style.background='rgba(0,0,0,0.6)';
            this.style.boxShadow='0 0 20px rgba(255,212,59,0.05)';
        };
        ci.onblur=function(){
            this.style.borderColor='rgba(255,255,255,0.06)';
            this.style.background='rgba(0,0,0,0.4)';
            this.style.boxShadow='none';
        };
        body.appendChild(ci);
        body.appendChild(document.createElement('br'));
        body.appendChild(document.createElement('br'));
        
        var cfg=document.createElement('div');
        cfg.style.cssText='display:flex;gap:12px;';
        var dg=document.createElement('div');
        dg.style.cssText='flex:1;';
        var dl=document.createElement('label');
        dl.innerHTML='<i class="fas fa-clock" style="margin-right:4px;color:#868e96;"></i> DELAY (ms):';
        dl.style.cssText='display:block;margin-bottom:4px;font-weight:600;font-size:10px;color:#868e96;letter-spacing:0.3px;text-transform:uppercase;';
        dg.appendChild(dl);
        var di=document.createElement('input');
        di.id='xrav-delay';
        di.type='number';
        di.value='3000';
        di.min='1000';
        di.max='10000';
        di.style.cssText='width:100%;padding:8px 12px;border:1px solid rgba(255,255,255,0.06);border-radius:8px;background:rgba(0,0,0,0.4);color:#e9ecef;font-size:13px;font-family:"Segoe UI", system-ui, sans-serif;box-sizing:border-box;outline:none;transition:all 0.3s;';
        di.onfocus=function(){
            this.style.borderColor='rgba(255,255,255,0.2)';
            this.style.background='rgba(0,0,0,0.6)';
        };
        di.onblur=function(){
            this.style.borderColor='rgba(255,255,255,0.06)';
            this.style.background='rgba(0,0,0,0.4)';
        };
        dg.appendChild(di);
        cfg.appendChild(dg);
        
        var ig=document.createElement('div');
        ig.style.cssText='flex:1;display:flex;align-items:center;justify-content:center;flex-direction:column;background:rgba(32,201,153,0.03);border-radius:8px;border:1px solid rgba(32,201,153,0.05);padding:4px;';
        var it=document.createElement('div');
        it.style.cssText='font-size:10px;color:#868e96;text-align:center;letter-spacing:0.3px;';
        it.innerHTML='<i class="fas fa-robot" style="font-size:20px;display:block;margin-bottom:2px;color:#20c997;"></i> DETECÇÃO AUTOMÁTICA';
        ig.appendChild(it);
        cfg.appendChild(ig);
        body.appendChild(cfg);
        body.appendChild(document.createElement('br'));
        
        var bc=document.createElement('div');
        bc.style.cssText='display:flex;gap:6px;flex-wrap:wrap;';
        var btn=document.createElement('button');
        btn.id='xrav-btn';
        btn.innerHTML='<i class="fas fa-play"></i> INICIAR';
        btn.style.cssText='flex:2;padding:12px 16px;background:#20c997;border:none;border-radius:8px;color:#000;font-weight:700;font-size:13px;font-family:"Segoe UI", system-ui, sans-serif;cursor:pointer;transition:all 0.3s;display:flex;align-items:center;justify-content:center;gap:8px;';
        btn.onmouseover=function(){
            this.style.transform='scale(1.02)';
            this.style.boxShadow='0 4px 20px rgba(32,201,153,0.3)';
        };
        btn.onmouseout=function(){
            this.style.transform='scale(1)';
            this.style.boxShadow='none';
        };
        btn.onclick=toggleScan;
        bc.appendChild(btn);
        var exp=document.createElement('button');
        exp.innerHTML='<i class="fas fa-file-export"></i> EXPORTAR';
        exp.style.cssText='flex:1;padding:12px 16px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:8px;color:#e9ecef;font-weight:600;font-size:12px;font-family:"Segoe UI", system-ui, sans-serif;cursor:pointer;transition:all 0.3s;display:flex;align-items:center;justify-content:center;gap:8px;';
        exp.onmouseover=function(){
            this.style.background='rgba(255,255,255,0.06)';
            this.style.borderColor='rgba(255,255,255,0.12)';
        };
        exp.onmouseout=function(){
            this.style.background='rgba(255,255,255,0.03)';
            this.style.borderColor='rgba(255,255,255,0.06)';
        };
        exp.onclick=exportTXT;
        bc.appendChild(exp);
        var clr=document.createElement('button');
        clr.innerHTML='<i class="fas fa-trash-alt"></i> LIMPAR';
        clr.style.cssText='flex:1;padding:12px 16px;background:rgba(255,107,107,0.05);border:1px solid rgba(255,107,107,0.06);border-radius:8px;color:#ff6b6b;font-weight:600;font-size:12px;font-family:"Segoe UI", system-ui, sans-serif;cursor:pointer;transition:all 0.3s;display:flex;align-items:center;justify-content:center;gap:8px;';
        clr.onmouseover=function(){
            this.style.background='rgba(255,107,107,0.1)';
            this.style.borderColor='rgba(255,107,107,0.15)';
        };
        clr.onmouseout=function(){
            this.style.background='rgba(255,107,107,0.05)';
            this.style.borderColor='rgba(255,107,107,0.06)';
        };
        clr.onclick=function(){
            clearLog();
            X.people=[];
            X.results=[];
            status('PRONTO');
        };
        bc.appendChild(clr);
        body.appendChild(bc);
        body.appendChild(document.createElement('br'));
        
        var lh=document.createElement('div');
        lh.style.cssText='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;';
        var ll=document.createElement('div');
        ll.innerHTML='<i class="fas fa-terminal" style="margin-right:6px;color:#868e96;"></i> LOG:';
        ll.style.cssText='font-weight:600;font-size:11px;color:#adb5bd;letter-spacing:0.3px;text-transform:uppercase;';
        lh.appendChild(ll);
        var lc=document.createElement('span');
        lc.id='xrav-log-count';
        lc.textContent='0 linhas';
        lc.style.cssText='font-size:10px;color:#868e96;';
        lh.appendChild(lc);
        body.appendChild(lh);
        var logEl=document.createElement('div');
        logEl.id='xrav-log';
        logEl.style.cssText='background:rgba(0,0,0,0.5);border-radius:8px;padding:10px 14px;max-height:180px;overflow-y:auto;font-family:"Consolas", "Courier New", monospace;font-size:11px;line-height:1.6;border:1px solid rgba(255,255,255,0.04);white-space:pre-wrap;word-wrap:break-word;color:#adb5bd;';
        logEl.textContent='> AGUARDANDO COMANDO...\n';
        body.appendChild(logEl);
        container.appendChild(body);
        
        var foot=document.createElement('div');
        foot.style.cssText='padding:8px 20px;background:rgba(0,0,0,0.2);border-top:1px solid rgba(255,255,255,0.03);font-size:9px;color:#868e96;text-align:center;cursor:default;flex-shrink:0;display:flex;justify-content:center;align-items:center;gap:16px;font-family:"Segoe UI", system-ui, sans-serif;letter-spacing:0.3px;';
        foot.innerHTML='<span><i class="fas fa-search" style="color:#20c997;margin-right:4px;"></i> XRAV</span><span><i class="fas fa-arrows-alt" style="margin-right:4px;"></i> ARRASTE</span><span><i class="fas fa-shield-alt" style="color:#4dabf7;margin-right:4px;"></i> SEGURO</span>';
        container.appendChild(foot);
        
        var drag=false, ox, oy;
        container.addEventListener('mousedown',function(e){
            if(e.target.closest('button')||e.target.closest('input'))return;
            drag=true;
            var r=container.getBoundingClientRect();
            ox=e.clientX-r.left;
            oy=e.clientY-r.top;
            container.style.cursor='grabbing';
            container.style.transition='none';
        });
        document.addEventListener('mousemove',function(e){
            if(!drag)return;
            var x=e.clientX-ox;
            var y=e.clientY-oy;
            x=Math.max(0,Math.min(window.innerWidth-container.offsetWidth,x));
            y=Math.max(0,Math.min(window.innerHeight-container.offsetHeight,y));
            container.style.left=x+'px';
            container.style.top=y+'px';
            container.style.right='auto';
        });
        document.addEventListener('mouseup',function(){
            if(drag){
                drag=false;
                container.style.cursor='move';
                container.style.transition='all 0.3s ease';
            }
        });
        
        document.body.appendChild(container);
        setTimeout(autoDetectName, 500);
    }
    
    console.log('XRAV JUSBR CARREGANDO...');
    if(document.getElementById('xrav-ui')) document.getElementById('xrav-ui').remove();
    createUI();
    console.log('XRAV JUSBR PRONTO');
    console.log('REALIZE A BUSCA NO JUSBRASIL PRIMEIRO');
})();
'''

def mostrar_banner():
    print(f"""{Cores.VERDE}╔══════════════════════════════════════════════════════════════╗
║                    XRAV JUSBR                                ║
╚══════════════════════════════════════════════════════════════╝{Cores.RESET}
""")

def main():
    parser = argparse.ArgumentParser(prog="xrav-jusbr", description="Gera script com interface hacker")
    parser.add_argument("--output", "-o", type=str, help="Salva o script em um arquivo específico")
    args = parser.parse_args()
    
    mostrar_banner()
    
    print(f"""{Cores.BRANCO}🔍 Detecta automaticamente o nome da pessoa pesquisada
🎯 Busca por CPFs específicos usando máscaras personalizadas
📊 Gera relatórios com todas as informações relevantes extraídas.
🏢 Identifica empresas e vínculos societários

{Cores.VERDE}╔══════════════════════════════════════════════════════════════╗
║                    INSTRUÇÕES DE USO                         ║
╚══════════════════════════════════════════════════════════════╝{Cores.RESET}

{Cores.BRANCO}1️. Acesse https://www.jusbrasil.com.br
2️. Faça a busca da pessoa desejada
3️. Pressione F12 → Abra a aba Console
4️. Cole TODO o script e pressione ENTER
5️. A interface aparecerá e detectará automaticamente
6️. Preencha a máscara CPF e clique em INICIAR

{Cores.MAGENTA}╔══════════════════════════════════════════════════════════════╗
║                    EXEMPLO DE MÁSCARA CPF                    ║
╚══════════════════════════════════════════════════════════════╝{Cores.RESET}

{Cores.BRANCO}📌 ***.123.123-** → Busca CPFs com os dígitos centrais
📌 123.123.123-** → Busca CPFs com os primeiros 9 dígitos fixos
📌 Use * (asterisco) para representar dígitos desconhecidos.

{Cores.VERMELHO}╔══════════════════════════════════════════════════════════════╗
║                    ATENÇÃO                                   ║
╚══════════════════════════════════════════════════════════════╝{Cores.RESET}

{Cores.AMARELO}⚠️  Respeite as leis e use apenas para fins legítimos
⚠️  O delay entre requisições evita sobrecarga no servidor
⚠️  Recomendado: delay mínimo de 1000ms entre requisições

{Cores.CIANO}╔══════════════════════════════════════════════════════════════╗
║                    ARQUIVO GERADO                            ║
╚══════════════════════════════════════════════════════════════╝{Cores.RESET}
""")
    
    gerador = GeradorDevToolsUI()
    script = gerador.gerar_script_ui()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome_arquivo = args.output if args.output else f'devtools-xrav-jusbr-{timestamp}.txt'
    if not nome_arquivo.endswith('.txt'): nome_arquivo += '.txt'
    
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write(script)
    
    print(f"""
{Cores.VERDE}✅ Script gerado com sucesso!{Cores.RESET}
{Cores.BRANCO}📁 Arquivo: {Cores.VERDE}{nome_arquivo}{Cores.RESET}
{Cores.BRANCO}📊 Tamanho: {Cores.AMARELO}{len(script):,}{Cores.RESET}{Cores.BRANCO} caracteres{Cores.RESET}

┌────────────────────────────────────────────────────┐
│ PRÓXIMOS PASSOS:                                   │
│ 1. Abra o arquivo gerado no editor de texto        │
│ 2. Selecione TODO o conteúdo (Ctrl+A)              │
│ 3. Copie (Ctrl+C)                                  │
│ 4. Cole no Console do navegador (Ctrl+V)           │
└────────────────────────────────────────────────────┘

{Cores.AMARELO}💡 Dica: Mantenha a aba do Jusbrasil ativa durante a execução
{Cores.BRANCO}
""")

if __name__ == "__main__":
    main()
