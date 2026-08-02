/* ═══ askakshay.com — shared sub-page chrome behaviour ═══ */
(function(){
'use strict';
// The sub-pages predate the redesign and each carries its own theme toggle
// writing to the same localStorage key. retheme.css is dark-only, so pin the
// attribute — otherwise a stale 'light' value leaves half the tokens unset.
document.documentElement.setAttribute('data-theme','dark');

var prog = document.querySelector('.ak-prog');
if (prog){
  var ticking = false;
  function onScroll(){
    var h = document.documentElement.scrollHeight - window.innerHeight;
    prog.style.width = (h > 0 ? (window.scrollY / h) * 100 : 0) + '%';
    ticking = false;
  }
  window.addEventListener('scroll', function(){
    if (!ticking){ ticking = true; requestAnimationFrame(onScroll); }
  }, {passive:true});
  onScroll();
}

var yr = document.querySelector('.ak-yr');
if (yr) yr.textContent = new Date().getFullYear();
})();
