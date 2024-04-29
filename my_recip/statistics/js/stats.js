function toggleSection(sectionId) {
    var element = document.getElementById(sectionId);
    // Check if the element is currently visible
    if (element.style.display === 'block' || element.classList.contains('visible')) {
        // Hide the element if it's visible
        element.style.display = 'none';
        element.classList.remove('visible');
    } else {
        // Show the element if it's hidden
        element.style.display = 'block';
        element.classList.add('visible');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/statistics')
    .then(response => response.json())
    .then(data => {
        const methodList = document.getElementById('methodList');
        methodList.innerHTML = data.methods.map(item => `<li>${item.method}: ${item.count}</li>`).join('');

        document.getElementById('registered').textContent = `Registered: ${data.registered.true}`;
        document.getElementById('nonRegistered').textContent = `Non-Registered: ${data.registered.false}`;

        const userAgentList = document.getElementById('userAgentList');
        userAgentList.innerHTML = data.top_user_agents.map(item => `<li>${item.user_agent}: ${item.count}</li>`).join('');

        const apiUsageList = document.getElementById('apiUsageList');
        // Update to reflect simplified data structure
        apiUsageList.innerHTML = data.api_usage.map(api => `
            <li>${api.api}: Total Requests - ${api.total_requests}</li>
        `).join('');
        
        const ipDetails = document.getElementById('ipDetails');
        ipDetails.innerHTML = data.ips.map(ip => `
            <div>
                <h3>${ip.ip}</h3>
                <p>Methods:</p>
                <ul>${ip.details.methods.map(method => `<li>${method.method}: ${method.count}</li>`).join('')}</ul>
                <p>Top User-Agents:</p>
                <ul>${ip.details.user_agents.map(ua => `<li>${ua.user_agent}: ${ua.count}</li>`).join('')}</ul>
            </div>
        `).join('');
    })
    .catch(error => console.error('Error fetching statistics:', error));
});

