document.addEventListener('DOMContentLoaded', function() {
    
    // --- 機能1：通知メッセージ（登録完了など）を自動で消す ---
    const flashMessages = document.querySelectorAll('.flash, .alert');
    
    if (flashMessages.length > 0) {
        // 3秒(3000ミリ秒)後にフワッと消える処理
        setTimeout(function() {
            flashMessages.forEach(function(msg) {
                msg.style.transition = "opacity 0.5s ease";
                msg.style.opacity = "0"; // 透明にする
                
                // 透明になった後に完全に削除する
                setTimeout(() => msg.remove(), 500);
            });
        }, 3000);
    }

    // --- 機能2：現在のページをメニューで強調表示する ---
    const currentUrl = window.location.href;
    const navLinks = document.querySelectorAll('nav a');

    navLinks.forEach(function(link) {
        // リンク先と今のURLが一致していたら 'active' クラスをつける
        if (link.href === currentUrl) {
            link.classList.add('active');
        }
    });

    // --- 機能3：数値入力フォームでマイナスが入らないようにする ---
    // (年齢や身長などで誤って「-」キーを押しても入力させない)
    const numberInputs = document.querySelectorAll('input[type="number"]');
    
    numberInputs.forEach(function(input) {
        input.addEventListener('keydown', function(e) {
            if (e.key === '-' || e.key === 'e') {
                e.preventDefault();
            }
        });
    });

});