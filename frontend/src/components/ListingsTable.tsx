import React from 'react';
import { ExternalLinkIcon } from '@heroicons/react/24/outline';

interface Listing {
  id: string;
  platform: string;
  title: string;
  make?: string;
  model?: string;
  year?: number;
  price?: number;
  currency: string;
  condition?: string;
  mileage?: number;
  location?: string;
  url: string;
  views: number;
  likes: number;
  comments: number;
  saves: number;
  shares: number;
  engagement_score: number;
  posted_date?: string;
  scraped_at: string;
}

interface ListingsTableProps {
  listings: Listing[];
}

const ListingsTable: React.FC<ListingsTableProps> = ({ listings }) => {
  const formatPrice = (price?: number, currency: string = 'MXN') => {
    if (!price) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(price);
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  const getPlatformBadge = (platform: string) => {
    const colors = {
      facebook: 'badge-primary',
      craigslist: 'badge-success',
      mercadolibre: 'badge-warning',
    };
    return colors[platform as keyof typeof colors] || 'badge-secondary';
  };

  const getConditionBadge = (condition?: string) => {
    if (!condition) return 'badge-secondary';
    const colors = {
      new: 'badge-success',
      used: 'badge-warning',
      certified: 'badge-primary',
      salvage: 'badge-danger',
    };
    return colors[condition as keyof typeof colors] || 'badge-secondary';
  };

  if (listings.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No listings found matching your criteria.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="table">
        <thead className="table-header">
          <tr>
            <th className="table-header-cell">Platform</th>
            <th className="table-header-cell">Title</th>
            <th className="table-header-cell">Make/Model</th>
            <th className="table-header-cell">Year</th>
            <th className="table-header-cell">Price</th>
            <th className="table-header-cell">Condition</th>
            <th className="table-header-cell">Mileage</th>
            <th className="table-header-cell">Engagement</th>
            <th className="table-header-cell">Posted</th>
            <th className="table-header-cell">Actions</th>
          </tr>
        </thead>
        <tbody className="table-body">
          {listings.map((listing) => (
            <tr key={listing.id} className="table-row">
              <td className="table-cell">
                <span className={`badge ${getPlatformBadge(listing.platform)}`}>
                  {listing.platform}
                </span>
              </td>
              <td className="table-cell">
                <div className="max-w-xs truncate" title={listing.title}>
                  {listing.title}
                </div>
              </td>
              <td className="table-cell">
                {listing.make && listing.model ? (
                  <span className="font-medium">
                    {listing.make} {listing.model}
                  </span>
                ) : (
                  <span className="text-gray-400">N/A</span>
                )}
              </td>
              <td className="table-cell">
                {listing.year || <span className="text-gray-400">N/A</span>}
              </td>
              <td className="table-cell">
                {formatPrice(listing.price, listing.currency)}
              </td>
              <td className="table-cell">
                {listing.condition ? (
                  <span className={`badge ${getConditionBadge(listing.condition)}`}>
                    {listing.condition}
                  </span>
                ) : (
                  <span className="text-gray-400">N/A</span>
                )}
              </td>
              <td className="table-cell">
                {listing.mileage ? (
                  <span>{listing.mileage.toLocaleString()} km</span>
                ) : (
                  <span className="text-gray-400">N/A</span>
                )}
              </td>
              <td className="table-cell">
                <div className="space-y-1">
                  <div className="text-sm font-medium">
                    Score: {listing.engagement_score.toLocaleString()}
                  </div>
                  <div className="text-xs text-gray-500">
                    V:{listing.views} L:{listing.likes} C:{listing.comments}
                  </div>
                </div>
              </td>
              <td className="table-cell">
                {formatDate(listing.posted_date)}
              </td>
              <td className="table-cell">
                <a
                  href={listing.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center text-blue-600 hover:text-blue-800"
                >
                  <ExternalLinkIcon className="h-4 w-4 mr-1" />
                  View
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ListingsTable;
