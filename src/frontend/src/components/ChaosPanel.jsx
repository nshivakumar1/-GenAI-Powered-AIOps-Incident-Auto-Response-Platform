import React, { useState } from 'react';

const ChaosPanel = ({ victimUrl }) => {
    const [loading, setLoading] = useState(false);
    const [msg, setMsg] = useState("");

    const triggerChaos = async (endpoint, type) => {
        setLoading(true);
        setMsg("");
        try {
            const res = await fetch(`${victimUrl}${endpoint}`, { method: 'POST' });
            const data = await res.json();
            setMsg(`✅ Triggered: ${type}`);
        } catch (e) {
            setMsg(`❌ Failed: ${e.message}`);
        }
        setLoading(false);
    };

    return (
        <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
                <button
                    onClick={() => triggerChaos('/simulate/cpu-spike', 'CPU Spike (P1)')}
                    disabled={loading}
                    className="p-4 bg-red-500/10 hover:bg-red-500/30 border border-red-500/50 rounded-lg text-red-400 font-bold transition-all flex flex-col items-center gap-2 group"
                >
                    <span className="text-2xl group-hover:scale-110 transition-transform">🔥</span>
                    Simulate CPU Spike
                </button>

                <button
                    onClick={() => triggerChaos('/simulate/memory-leak', 'Memory Leak (P2)')}
                    disabled={loading}
                    className="p-4 bg-purple-500/10 hover:bg-purple-500/30 border border-purple-500/50 rounded-lg text-purple-400 font-bold transition-all flex flex-col items-center gap-2 group"
                >
                    <span className="text-2xl group-hover:scale-110 transition-transform">💧</span>
                    Simulate Memory Leak
                </button>
            </div>

            <button
                onClick={() => triggerChaos('/reset', 'System Reset')}
                disabled={loading}
                className="w-full py-3 bg-green-500/10 hover:bg-green-500/30 border border-green-500/50 rounded-lg text-green-400 font-bold transition-all"
            >
                ♻️ Reset System State
            </button>

            {msg && (
                <div className="text-center text-sm font-mono text-gray-300 animate-fade-in">
                    {msg}
                </div>
            )}
        </div>
    );
};

export default ChaosPanel;
