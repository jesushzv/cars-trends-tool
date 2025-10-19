import React from 'react';
import { Icon } from '@heroicons/react/24/outline';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: Icon;
  color: 'blue' | 'green' | 'red' | 'purple' | 'yellow' | 'indigo';
  change?: {
    value: number;
    type: 'increase' | 'decrease';
  };
  subtitle?: string;
}

const StatCard: React.FC<StatCardProps> = ({ 
  title, 
  value, 
  icon: Icon, 
  color, 
  change, 
  subtitle 
}) => {
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-100',
    green: 'text-green-600 bg-green-100',
    red: 'text-red-600 bg-red-100',
    purple: 'text-purple-600 bg-purple-100',
    yellow: 'text-yellow-600 bg-yellow-100',
    indigo: 'text-indigo-600 bg-indigo-100',
  };

  return (
    <div className="stat-card">
      <div className="flex items-center">
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="h-6 w-6" />
        </div>
        <div className="ml-4 flex-1">
          <p className="stat-label">{title}</p>
          <p className="stat-value">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          )}
          {change && (
            <p className={`stat-change ${
              change.type === 'increase' ? 'stat-change-positive' : 'stat-change-negative'
            }`}>
              {change.type === 'increase' ? '+' : '-'}{Math.abs(change.value)}%
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default StatCard;
