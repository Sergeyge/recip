function toggleSection(sectionId) {
    var element = document.getElementById(sectionId);
    if (element.style.display === 'block' || element.classList.contains('visible')) {
        element.style.display = 'none';
        element.classList.remove('visible');
    } else {
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

