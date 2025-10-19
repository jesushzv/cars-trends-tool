import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface PriceTrendsChartProps {
  data: Array<{
    date: string;
    avg_price: number;
    min_price: number;
    max_price: number;
    total_listings: number;
  }>;
}

const PriceTrendsChart: React.FC<PriceTrendsChartProps> = ({ data }) => {
  const chartData = {
    labels: data.map(item => new Date(item.date).toLocaleDateString()),
    datasets: [
      {
        label: 'Average Price',
        data: data.map(item => item.avg_price),
        borderColor: 'rgba(59, 130, 246, 1)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true,
      },
      {
        label: 'Min Price',
        data: data.map(item => item.min_price),
        borderColor: 'rgba(34, 197, 94, 1)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4,
        borderDash: [5, 5],
      },
      {
        label: 'Max Price',
        data: data.map(item => item.max_price),
        borderColor: 'rgba(239, 68, 68, 1)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4,
        borderDash: [5, 5],
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const item = data[context.dataIndex];
            return [
              `${context.dataset.label}: $${context.parsed.y.toLocaleString()}`,
              `Listings: ${item.total_listings}`,
            ];
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value: any) {
            return `$${value.toLocaleString()}`;
          },
        },
      },
      x: {
        ticks: {
          maxRotation: 45,
          minRotation: 45,
        },
      },
    },
  };

  return (
    <div className="chart-responsive">
      <Line data={chartData} options={options} />
    </div>
  );
};

export default PriceTrendsChart;
