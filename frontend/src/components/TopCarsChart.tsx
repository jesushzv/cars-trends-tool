import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface TopCarsChartProps {
  data: Array<{
    make: string;
    model: string;
    engagement_score: number;
    total_listings: number;
    total_views: number;
    total_likes: number;
    total_comments: number;
  }>;
}

const TopCarsChart: React.FC<TopCarsChartProps> = ({ data }) => {
  const chartData = {
    labels: data.map(car => `${car.make} ${car.model}`),
    datasets: [
      {
        label: 'Engagement Score',
        data: data.map(car => car.engagement_score),
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          afterLabel: function(context: any) {
            const car = data[context.dataIndex];
            return [
              `Listings: ${car.total_listings}`,
              `Views: ${car.total_views.toLocaleString()}`,
              `Likes: ${car.total_likes.toLocaleString()}`,
              `Comments: ${car.total_comments.toLocaleString()}`,
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
            return value.toLocaleString();
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
      <Bar data={chartData} options={options} />
    </div>
  );
};

export default TopCarsChart;
