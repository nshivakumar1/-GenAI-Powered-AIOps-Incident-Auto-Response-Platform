import React from 'react';

// For the demo, we mock incidents since we can't easily query ES from client without CORS proxy
const MOCK_INCIDENTS = [
    {
        id: "INC-1024",
        time: "2 mins ago",
        severity: "P1",
        category: "app",
        root_cause: "CPU Spike detected in payment-service container.",
        status: "RESOLVED"
    },
    {
        id: "INC-1023",
        time: "15 mins ago",
        severity: "P2",
        category: "db",
        root_cause: "Connection pool exhaustion > 80%",
        status: "AUTO-FIXED"
    }
];

const IncidentFeed = () => {
    return (
        <div className="flex-1 overflow-y-auto pr-2 space-y-4">
            {MOCK_INCIDENTS.map((inc) => (
                <div key={inc.id} className="bg-black/20 p-4 rounded-lg border border-gray-700 hover:border-blue-500/50 transition-colors">
                    <div className="flex justify-between items-start mb-2">
                        <span className={`px-2 py-0.5 rounded text-xs font-bold ${inc.severity === 'P1' ? 'bg-red-500 text-white' : 'bg-orange-400 text-black'
                            }`}>
                            {inc.severity}
                        </span>
                        <span className="text-xs text-gray-500">{inc.time}</span>
                    </div>

                    <h3 className="font-semibold text-gray-200 mb-1">{inc.root_cause}</h3>

                    <div className="flex justify-between items-center text-xs mt-3">
                        <span className="text-gray-400 font-mono">ID: {inc.id}</span>
                        <span className="text-green-400 font-bold flex items-center gap-1">
                            ✅ {inc.status}
                        </span>
                    </div>
                </div>
            ))}

            <div className="text-center text-gray-600 text-sm py-4 italic">
                Listening for new CloudWatch Alerts...
            </div>
        </div>
    );
};

export default IncidentFeed;
