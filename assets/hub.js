/* ═══ askakshay.com — shared hub page behaviour ═══ */
(function(){
'use strict';
var RM = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

var revs = [].slice.call(document.querySelectorAll('.rv'));

/* IntersectionObserver callbacks are throttled in hidden/background tabs, so a
   page opened with cmd-click and read later can land on opacity:0 blocks. This
   sweep runs off the same rAF scroll tick and reveals anything already at or
   above the viewport bottom, regardless of whether IO has fired for it. */
function sweepReveal(){
  if (!revs.length) return;
  var limit = window.innerHeight;
  revs = revs.filter(function(e){
    if (e.getBoundingClientRect().top < limit){ e.classList.add('in'); return false; }
    return true;
  });
}

var prog = document.getElementById('prog'), ticking = false;
function onScroll(){
  if (prog){
    var h = document.documentElement.scrollHeight - window.innerHeight;
    prog.style.width = (h > 0 ? (window.scrollY / h) * 100 : 0) + '%';
  }
  sweepReveal();
  ticking = false;
}
window.addEventListener('scroll', function(){
  if (!ticking){ ticking = true; requestAnimationFrame(onScroll); }
}, {passive:true});
// rAF is suspended while the tab is hidden, so a scroll on the way out latches
// `ticking` at true and the callback that clears it never runs — the progress
// bar then stays frozen for the rest of the session.
document.addEventListener('visibilitychange', function(){
  if (document.visibilityState === 'visible'){ ticking = false; onScroll(); }
});

if (RM || !('IntersectionObserver' in window)){
  revs.forEach(function(e){ e.classList.add('in'); });
  revs = [];
} else {
  var ro = new IntersectionObserver(function(es){
    es.forEach(function(en){
      if (en.isIntersecting){
        en.target.classList.add('in');
        ro.unobserve(en.target);
        revs = revs.filter(function(e){ return e !== en.target; });
      }
    });
  }, {rootMargin:'0px 0px -8% 0px', threshold:0});
  revs.forEach(function(e){ ro.observe(e); });
  document.addEventListener('visibilitychange', function(){
    if (document.visibilityState === 'visible') sweepReveal();
  });
}

onScroll();

var yr = document.getElementById('yr');
if (yr) yr.textContent = new Date().getFullYear();
})();
