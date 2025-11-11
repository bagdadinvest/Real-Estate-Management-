(function(){
  function bindSwitcher(root){
    var btn = root.querySelector('.lang-current');
    var menu = root.querySelector('.lang-menu');
    if (!btn || !menu) return;

    function open(){ root.classList.add('open'); btn.setAttribute('aria-expanded','true'); }
    function close(){ root.classList.remove('open'); btn.setAttribute('aria-expanded','false'); }
    function toggle(){ root.classList.contains('open') ? close() : open(); }

    btn.addEventListener('click', function(e){ e.stopPropagation(); toggle(); });
    menu.addEventListener('click', function(e){ e.stopPropagation(); });
    document.addEventListener('click', function(){ close(); });
    document.addEventListener('keydown', function(e){ if (e.key === 'Escape') close(); });
  }

  document.addEventListener('DOMContentLoaded', function(){
    var all = document.querySelectorAll('.lang-switcher');
    all.forEach(bindSwitcher);
  });
})();
