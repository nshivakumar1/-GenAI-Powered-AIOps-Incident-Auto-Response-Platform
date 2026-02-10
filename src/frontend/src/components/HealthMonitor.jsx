import React from 'react';

const HealthMonitor = ({ data }) => {
    if (!data || data.status === 'disconnected') {
        return (
            <div className="animate-pulse flex flex-col gap-4">
                <div className="h-4 bg-gray-700 rounded w-3/4"></div>
                <div className="h-4 bg-gray-700 rounded w-1/2"></div>
                <p className="text-red-400 text-sm mt-2">Cannot reach Victim Service. Ensure Docker container is running on port 8000.</p>
            </div>
        );
    }

    const cpu = data.cpu || 0;
    const memory = data.memory || 0;

    return (
        <div className="space-y-6">

            {/* CPU Bar */}
            <div>
                <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium text-gray-300">CPU Usage</span>
                    <span className={`text-sm font-medium ${cpu > 80 ? 'text-red-400' : 'text-blue-400'}`}>
                        {cpu}%
                    </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2.5">
                    <div
                        className={`h-2.5 rounded-full transition-all duration-500 ${cpu > 80 ? 'bg-red-500' : 'bg-blue-500'}`}
                        style={{ width: `${cpu}%` }}
                    ></div>
                </div>
            </div>

            {/* Memory Bar */}
            <div>
                <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium text-gray-300">Memory Usage</span>
                    <span className={`text-sm font-medium ${memory > 80 ? 'text-red-400' : 'text-purple-400'}`}>
                        {memory}%
                    </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2.5">
                    <div
                        className={`h-2.5 rounded-full transition-all duration-500 ${memory > 80 ? 'bg-red-500' : 'bg-purple-500'}`}
                        style={{ width: `${memory}%` }}
                    ></div>
                </div>
            </div>

            {/* Status Details */}
            <div className="bg-black/30 p-3 rounded text-xs font-mono text-gray-400">
                Status: <span className={data.status === 'healthy' ? 'text-green-400' : 'text-red-400'}>{data.status}</span>
                {data.reason && <div className="text-red-400 mt-1">Reason: {data.reason}</div>}
            </div>

        </div>
    );
};

export default HealthMonitor;
