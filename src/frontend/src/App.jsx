import React, { useState, useEffect } from 'react';
import ChaosPanel from './components/ChaosPanel';
import HealthMonitor from './components/HealthMonitor';
import IncidentFeed from './components/IncidentFeed';

/**
 * Root React component for the AIOps Incident Command UI.
 *
 * Polls the victim service health endpoint (/api/health) every 2 seconds to keep local health state up to date,
 * and renders the application's header (with a status badge), live telemetry, chaos engineering controls, and incident feed.
 *
 * @returns {JSX.Element} The rendered application UI.
 */
function App() {
    const [healthData, setHealthData] = useState(null);
    const [incidents, setIncidents] = useState([]);

    const VICTIM_SERVICE_URL = "/api"; // Requests routed via ALB

    // Poll Health
    useEffect(() => {
        const interval = setInterval(async () => {
            try {
                const res = await fetch(`${VICTIM_SERVICE_URL}/health`);
                const data = await res.json();
                setHealthData(data);
            } catch (e) {
                setHealthData({ status: "disconnected" });
            }
        }, 2000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="min-h-screen bg-gray-900 text-white font-sans p-8">
            <header className="mb-10 flex justify-between items-center border-b border-gray-700 pb-4">
                <div>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
                        AIOps Incident Command
                    </h1>
                    <p className="text-gray-400 mt-1">GenAI-Powered Self-Healing System</p>
                </div>
                <div className={`px-4 py-2 rounded-full font-bold ${healthData?.status === 'healthy' ? 'bg-green-500/20 text-green-400' :
                    healthData?.status === 'disconnected' ? 'bg-gray-700 text-gray-400' :
                        'bg-red-500/20 text-red-500'
                    }`}>
                    System Status: {healthData?.status?.toUpperCase() || 'CONNECTING...'}
                </div>
            </header>

            <main className="grid grid-cols-1 md:grid-cols-2 gap-8">

                {/* Left Column: Controls & Metrics */}
                <div className="space-y-8">
                    <section className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg">
                        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                            📊 Live Telemetry
                        </h2>
                        <HealthMonitor data={healthData} />
                    </section>

                    <section className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg">
                        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                            🧪 Chaos Engineering
                        </h2>
                        <ChaosPanel victimUrl={VICTIM_SERVICE_URL} />
                    </section>
                </div>

                {/* Right Column: Incident Feed */}
                <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg h-[600px] overflow-hidden flex flex-col">
                    <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                        🚨 Incident Feed (Real-time)
                    </h2>
                    <IncidentFeed />
                </div>

            </main>
        </div>
    );
}

export default App;