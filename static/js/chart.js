// グラフを描く場所を指定
const ctx = document.getElementById('dailyCalorieChart').getContext('2d');

// 今はテストデータを入れています（後でPythonから本物のデータを渡せます）
const labels = ['1/10', '1/11', '1/12', '1/13', '1/14', '1/15']; 
const intakeData = [1800, 1200, 1500, 2300, 1900, 1700]; // 摂取カロリー（黄色）
const burnedData = [500, 300, 450, 700, 550, 400];    // 消費カロリー（赤色）
const targetCalorie = 1500; // 目標摂取カロリー（青色の横線）

const dailyCalorieChart = new Chart(ctx, {
    data: {
        labels: labels,
        datasets: [
            {
                type: 'line', // これだけ折れ線（目標線）
                label: '目標摂取カロリー',
                data: Array(labels.length).fill(targetCalorie),
                borderColor: '#5dade2', // 青色
                borderWidth: 3,
                fill: false,
                pointRadius: 5,
                order: 1 // 一番手前に表示
            },
            {
                type: 'bar', // 棒グラフ（摂取）
                label: '摂取カロリー',
                data: intakeData,
                backgroundColor: '#f9d976', // 黄色
                order: 2
            },
            {
                type: 'bar', // 棒グラフ（消費）
                label: '消費カロリー',
                data: burnedData,
                backgroundColor: '#f1948a', // 赤色
                order: 2
            }
        ]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true,
                title: { display: true, text: 'カロリー (kcal)' }
            }
        }
    }
});