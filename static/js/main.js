document.addEventListener('DOMContentLoaded', function() {

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

//ユーザー設定ページ(settings.html)の登録後3秒後に自動で閉じる
document.addEventListener('DOMContentLoaded', function() {

    const settingsForm = document.querySelector('.settings-container form');
    
    if (settingsForm) {
        settingsForm.addEventListener('submit', function() {
            setTimeout(function() {
            // 3秒後にダッシュボードへ移動する
            window.location.href = "{{ url_for('dashboard') }}";
        }, 3000);
        });
    }
});