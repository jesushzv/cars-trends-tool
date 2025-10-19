import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { listingsService } from '../services/listingsService';
import LoadingSpinner from '../components/LoadingSpinner';
import ListingFilters from '../components/ListingFilters';
import ListingsTable from '../components/ListingsTable';

const Listings: React.FC = () => {
  const [filters, setFilters] = useState({
    platform: '',
    make: '',
    model: '',
    min_price: '',
    max_price: '',
    min_year: '',
    max_year: '',
    condition: '',
    days_back: 30,
  });

  const { data: listings, isLoading, error } = useQuery(
    ['listings', filters],
    () => listingsService.getListings(filters),
    {
      keepPreviousData: true,
    }
  );

  const handleFiltersChange = (newFilters: any) => {
    setFilters(newFilters);
  };

  if (isLoading) {
    return <LoadingSpinner className="min-h-96" />;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Failed to load listings</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Car Listings</h1>
        <p className="text-gray-600">Browse and filter car listings from all platforms</p>
      </div>

      {/* Filters */}
      <div className="card">
        <ListingFilters filters={filters} onFiltersChange={handleFiltersChange} />
      </div>

      {/* Listings Table */}
      <div className="card">
        <ListingsTable listings={listings || []} />
      </div>
    </div>
  );
};

export default Listings;
