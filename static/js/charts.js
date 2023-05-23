var ctx1 = document.getElementById('bookingTrend1').getContext('webgl');
var myChart1 = new Chart(ctx1, {
    type: 'line',
    data: {
        labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
        datasets: [{
            label: 'Booking Trend',
            data: [10, 12, 8, 15, 20, 18, 25],
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
        }]
    },
    options: {
        plugins: {
            title: {
                display: true,
                text: 'Booking Trend',
                font: {
                    size: 16
                }
            }
        }
    }
});

var ctx2 = document.getElementById('topRoom1').getContext('webgl');
var myChart2 = new Chart(ctx2, {
    type: 'bar',
    data: {
        labels: ['Single Room', 'Double Room', 'Suite'],
        datasets: [{
            label: 'Number of Bookings',
            data: [50, 35, 20],
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)'
            ],
            borderWidth: 1
        }]
    },
    options: {
        plugins: {
            title: {
                display: true,
                text: 'Top Rooms',
                font: {
                    size: 16
                }
            }
        }
    }
});
