import React, { useState, useEffect } from 'react';

const IncidentFeed = () => {
    const [incidents, setIncidents] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchIncidents = async () => {
            try {
                const res = await fetch('/api/incidents');
                if (res.ok) {
                    const data = await res.json();
                    setIncidents(data);
                }
            } catch (e) {
                console.error("Failed to fetch incidents", e);
            } finally {
                setLoading(false);
            }
        };

        fetchIncidents();
        // Poll every 10 seconds
        const interval = setInterval(fetchIncidents, 10000);
        return () => clearInterval(interval);
    }, []);

    if (loading && incidents.length === 0) {
        return <div className="text-gray-400 text-center py-4">Loading incidents...</div>;
    }

    return (
        <div className="flex-1 overflow-y-auto pr-2 space-y-4">
            {incidents.length === 0 ? (
                <div className="text-center text-gray-500 py-8">No active incidents found.</div>
            ) : (
                incidents.map((inc) => (
                    <div key={inc.id} className="bg-black/20 p-4 rounded-lg border border-gray-700 hover:border-blue-500/50 transition-colors">
                        <div className="flex justify-between items-start mb-2">
                            <span className={`px-2 py-0.5 rounded text-xs font-bold ${inc.severity === 'P1' || inc.priority === 'High' ? 'bg-red-500 text-white' : 'bg-orange-400 text-black'
                                }`}>
                                {inc.severity || inc.priority || 'P?'}
                            </span>
                            <span className="text-xs text-gray-500">{inc.time || 'Just now'}</span>
                        </div>

                        <h3 className="font-semibold text-gray-200 mb-1">{inc.root_cause || inc.summary}</h3>

                        <div className="flex justify-between items-center text-xs mt-3">
                            <span className="text-gray-400 font-mono">ID: {inc.key || inc.id}</span>
                            <span className={`font-bold flex items-center gap-1 ${inc.status === 'Resolved' || inc.status === 'Closed' ? 'text-green-400' : 'text-yellow-400'}`}>
                                {inc.status === 'Resolved' ? '✅' : '⚠️'} {inc.status?.toUpperCase()}
                            </span>
                        </div>
                    </div>
                ))
            )}
        </div>
    );
};

export default IncidentFeed;
