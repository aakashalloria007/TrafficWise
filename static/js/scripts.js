// Simulated traffic data
const trafficData = {
    "1": { title: "Downtown Route", prediction: "Heavy traffic expected.", trafficGraph: [15, 25, 35, 45, 55, 65] },
    "2": { title: "Airport Route", prediction: "Light traffic.", trafficGraph: [10, 15, 20, 25, 30, 35] },
    "3": { title: "Suburbs Route", prediction: "Moderate traffic.", trafficGraph: [20, 30, 40, 50, 60, 70] }
};



// Traffic Prediction Chart (Dashboard)
window.onload = function() {
    if (window.location.pathname.includes("dashboard")) {
        const ctx = document.getElementById('trafficChart').getContext('2d');
        const trafficChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['9 AM', '10 AM', '11 AM', '12 PM', '1 PM', '2 PM'],
                datasets: [{
                    label: 'Traffic Flow',
                    data: [30, 40, 50, 70, 60, 80],
                    borderColor: '#3498db',
                    fill: false
                }]
            }
        });
    }

    if (window.location.pathname.includes("route-details.html")) {
        const urlParams = new URLSearchParams(window.location.search);
        const routeId = urlParams.get('route');
        if (trafficData[routeId]) {
            document.getElementById('route-title').textContent = trafficData[routeId].title;
            document.getElementById('route-prediction').textContent = trafficData[routeId].prediction;

            // Graph for route prediction over time
            const ctx = document.getElementById('trafficPredictionGraph').getContext('2d');
            const trafficGraph = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['9 AM', '10 AM', '11 AM', '12 PM', '1 PM', '2 PM'],
                    datasets: [{
                        label: 'Traffic Prediction',
                        data: trafficData[routeId].trafficGraph,
                        borderColor: '#2ecc71',
                        fill: false
                    }]
                }
            });
        }
    }
};

// Filter routes by traffic condition
function filterRoutes() {
    const filter = document.getElementById('route-filter').value;
    const routes = document.getElementById('route-list');
    routes.innerHTML = '';

    Object.keys(trafficData).forEach(routeId => {
        const route = trafficData[routeId];
        if (filter === 'all' || (filter === 'heavy' && route.prediction.includes('Heavy')) ||
            (filter === 'light' && route.prediction.includes('Light'))) {

            const li = document.createElement('li');
            li.innerHTML = `<a href="route-details.html?route=${routeId}">${route.title}</a>`;
            routes.appendChild(li);
        }
    });
}
