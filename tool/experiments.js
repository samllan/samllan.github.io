'use strict';
const laneReveal = document.querySelector('#lane-reveal');
if (laneReveal) laneReveal.addEventListener('input', () => {
  document.querySelector('#lane-overlay').style.clipPath = `inset(0 ${100-Number(laneReveal.value)}% 0 0)`;
});
const ns = 'http://www.w3.org/2000/svg';
function el(tag, attrs, parent) { const item = document.createElementNS(ns, tag); for (const [k,v] of Object.entries(attrs)) item.setAttribute(k,v); parent.append(item); return item; }
const plot = document.querySelector('#fourier');
if (plot) {
  const slider = document.querySelector('#harmonics');
  function draw() {
    plot.replaceChildren();
    const count = Number(slider.value); document.querySelector('#harmonic-count').value = count;
    const wave = (x, n) => 0.57*Math.sin(x-1.4) + (n>=2 ? .22*Math.cos(2*x+.3):0) + (n>=3 ? .11*Math.sin(3*x-1):0) + (n>=4 ? .06*Math.cos(4*x+.8):0);
    for(let row=0; row<5; row++) el('line',{x1:35,y1:25+row*65,x2:865,y2:25+row*65,stroke:'#d5d5c9'},plot);
    for(const [n,stroke,width] of [[4,'#aaa79c',3],[count,'#435e48',4]]) {
      const d = Array.from({length:361},(_,i)=>`${i?'L':'M'}${35+i*830/360},${165-wave(i/360*Math.PI*2,n)*140}`).join(' ');
      el('path',{d,fill:'none',stroke,'stroke-width':width},plot);
    }
    ['Jan','Apr','Jul','Oct','Jan'].forEach((month,i)=>{el('text',{x:35+i*207.5,y:325,fill:'#647063','font-size':13,'text-anchor':i===4?'end':'start'},plot).textContent=month;});
  }
  slider.addEventListener('input',draw); draw();
}
const rain = document.querySelector('#rain');
if (rain) {
  const play = document.querySelector('#play'), reset = document.querySelector('#reset'), status = document.querySelector('#music-status');
  let notes=[], duration=24, position=0, base=0, running=false, ctx, active=[];
  const low=36, high=84, width=900/(high-low+1);
  function stopAudio(){ for(const voice of active) { try{voice.stop();}catch{} } active=[]; }
  function draw(){
    rain.replaceChildren();
    for(let pitch=low;pitch<=high;pitch++){
      const black=[1,3,6,8,10].includes(pitch%12), x=(pitch-low)*width;
      el('line',{x1:x,y1:15,x2:x,y2:308,stroke:'#ffffff0d'},rain);
      const sounding=running&&notes.some(n=>n.pitch===pitch&&n.start<=position&&n.start+n.duration>position);
      el('rect',{x:x+1,y:310,width:width-2,height:42,rx:2,fill:sounding?'#bce5d7':black?'#55505f':'#ece6f0'},rain);
    }
    for(const note of notes){
      const bottom=310-(note.start-position)*62, h=Math.max(4,note.duration*62);
      if(bottom<0||bottom-h>310)continue;
      el('rect',{x:(note.pitch-low)*width+2,y:Math.max(4,bottom-h),width:width-4,height:Math.max(0,Math.min(310,bottom)-Math.max(4,bottom-h)),rx:3,fill:note.pitch<60?'#98cdbb':'#d4b8ef'},rain);
    }
    el('line',{x1:0,y1:309,x2:900,y2:309,stroke:'#e3d2a9','stroke-width':2},rain);
    if(running){ position=Math.min(duration,ctx.currentTime-base); status.textContent=`${position.toFixed(1)} / ${duration} seconds · synthesised sound`; if(position>=duration){running=false;position=0;play.textContent='Play again';stopAudio();} else requestAnimationFrame(draw); }
  }
  function schedule(){
    for(const n of notes){
      if(n.start+n.duration<=position)continue;
      const start=ctx.currentTime+Math.max(0,n.start-position), length=Math.max(.02,n.duration-Math.max(0,position-n.start));
      const voice=ctx.createOscillator(), gain=ctx.createGain(); voice.type='triangle';voice.frequency.value=440*Math.pow(2,(n.pitch-69)/12);
      gain.gain.setValueAtTime(0,start);gain.gain.linearRampToValueAtTime(.07,start+.02);gain.gain.exponentialRampToValueAtTime(.001,start+length+.12);
      voice.connect(gain);gain.connect(ctx.destination);voice.onended=()=>{voice.disconnect();gain.disconnect();active=active.filter(v=>v!==voice);};voice.start(start);voice.stop(start+length+.15);active.push(voice);
    }
  }
  play.addEventListener('click',async()=>{
    try{
      if(running){position=ctx.currentTime-base;running=false;stopAudio();play.textContent='Resume';draw();return;}
      ctx??=new AudioContext();await ctx.resume();base=ctx.currentTime-position;running=true;schedule();play.textContent='Pause';draw();
    }catch{running=false;status.textContent='Audio is unavailable in this browser.';play.textContent='Play demo';}
  });
  reset.addEventListener('click',()=>{running=false;position=0;stopAudio();play.textContent='Play demo';status.textContent='24-second practice pattern · synthesised sound';draw();});
  document.addEventListener('visibilitychange',()=>{if(document.hidden&&running){position=ctx.currentTime-base;running=false;stopAudio();play.textContent='Resume';}});
  fetch('../assets/music-demo.json').then(r=>{if(!r.ok)throw Error();return r.json();}).then(data=>{notes=data.notes;duration=data.duration;play.disabled=false;play.textContent='Play demo';draw();}).catch(()=>{status.textContent='The demo could not load. Please refresh the page.';play.textContent='Demo unavailable';});
}
