import React from 'react';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { Doughnut } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend);

interface MarketShareChartProps {
  data: Array<{
    name: string;
    count: number;
    percentage: number;
    avg_price: number;
    total_engagement: number;
  }>;
}

const MarketShareChart: React.FC<MarketShareChartProps> = ({ data }) => {
  const colors = [
    'rgba(59, 130, 246, 0.8)',
    'rgba(34, 197, 94, 0.8)',
    'rgba(239, 68, 68, 0.8)',
    'rgba(168, 85, 247, 0.8)',
    'rgba(245, 158, 11, 0.8)',
    'rgba(236, 72, 153, 0.8)',
    'rgba(14, 165, 233, 0.8)',
    'rgba(34, 197, 94, 0.8)',
  ];

  const chartData = {
    labels: data.map(item => item.name),
    datasets: [
      {
        data: data.map(item => item.count),
        backgroundColor: colors,
        borderColor: colors.map(color => color.replace('0.8', '1')),
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const,
        labels: {
          usePointStyle: true,
          padding: 20,
        },
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const item = data[context.dataIndex];
            return [
              `${item.name}: ${item.count} listings`,
              `${item.percentage}% of market`,
              `Avg Price: $${item.avg_price?.toLocaleString() || 'N/A'}`,
            ];
          },
        },
      },
    },
  };

  return (
    <div className="chart-responsive">
      <Doughnut data={chartData} options={options} />
    </div>
  );
};

export default MarketShareChart;
