/* askakshay.com design system layer: scroll reveal with failsafes. */
(function(){
'use strict';
if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
var els = [].slice.call(document.querySelectorAll('.ak-next a, article h2, article blockquote, article figure, .data-block, .callout, .pull'));
if (!els.length) return;
els.forEach(function(e){ e.classList.add('ak-rv'); });
function show(e){ e.classList.add('in'); }
// IntersectionObserver is throttled in background tabs and rAF is suspended there,
// so a scroll-position sweep on setTimeout plus a hard timeout guarantee nothing stays hidden.
function sweep(){
  var lim = window.innerHeight * 1.05;
  els = els.filter(function(e){ if (e.getBoundingClientRect().top < lim){ show(e); return false; } return true; });
}
var t;
window.addEventListener('scroll', function(){ clearTimeout(t); t = setTimeout(sweep, 30); }, {passive:true});
window.addEventListener('resize', sweep);
sweep();
var poll = setInterval(function(){ sweep(); if (!els.length) clearInterval(poll); }, 200);
setTimeout(function(){ els.forEach(show); els = []; clearInterval(poll); }, 4000);
})();
