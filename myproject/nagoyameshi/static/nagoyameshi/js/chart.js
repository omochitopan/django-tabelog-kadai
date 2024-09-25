let months_list = months.map(num => {
    const numStr = num.toString();
    const year = numStr.slice(0, 4);
    const month = numStr.slice(4);
    return `${year}年${month}月`;
});

const ctx = document.getElementById('counts').getContext('2d');
if (method === 1) {
    const user_chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months_list,
            datasets: [{
                label: "会員総数",
                data: active_counts,
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                fill: false
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    },
                    title: {
                        display: true,
                        text: '会員総数'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
} else if (method === 2) {
    const user_chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months_list,
            datasets: [
                {
                    label: '有料会員総数',
                    data: subscriber_counts,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    fill: false
                },
                {
                    label: '無料会員総数',
                    data: free_counts,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 2,
                    fill: false
                }
            ]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    },
                    title: {
                        display: true,
                        text: '有料・無料会員総数'
                    }
                }
            }
        }
    });
} else if (method === 3) {
    const user_chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: months_list,
            datasets: [
                {
                    label: '入会者数',
                    data: join_counts,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    fill: false
                },
                {
                    label: '退会者数',
                    data: leave_counts,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 2,
                    fill: false
                }
            ]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    },
                    title: {
                        display: true,
                        text: '各月入会・退会者数'
                    }
                }
            }
        }
    });
} else if (method === 4) {
    const restaurant_chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months_list,
            datasets: [
                {
                    label: '営業中店舗総数',
                    data: open_counts,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    fill: false
                },
                {
                    label: '閉店済店舗総数',
                    data: closed_counts,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 2,
                    fill: false
                }
            ]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    },
                    title: {
                        display: true,
                        text: '店舗総数'
                    }
                }
            }
        }
    });
} else if (method === 5) {
    const restaurant_chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: months_list,
            datasets: [
                {
                    label: '開店店舗数',
                    data: monthly_open_counts,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    fill: false
                },
                {
                    label: '閉店店舗数',
                    data: monthly_closed_counts,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 2,
                    fill: false
                }
            ]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    },
                    title: {
                        display: true,
                        text: '各月遷移店舗数'
                    }
                }
            }
        }
    });
} else if (method === 6) {
    const reservation_chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: months_list,
            datasets: [
                {
                    label: restaurant_name,
                    data: reservation_counts,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    fill: false
                }
            ]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 5
                    },
                    title: {
                        display: true,
                        text: '各月予約数'
                    }
                }
            }
        }
    });
} else if (method === 7) {
    const sales_chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: months_list,
            datasets: [
                {
                    label: "各月売上金額",
                    data: sales_counts,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    fill: false
                }
            ]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 100
                    },
                    title: {
                        display: true,
                        text: '売上金額'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}
