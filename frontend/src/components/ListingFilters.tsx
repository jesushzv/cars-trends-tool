import React from 'react';
import { useForm } from 'react-hook-form';

interface ListingFiltersProps {
  filters: any;
  onFiltersChange: (filters: any) => void;
}

const ListingFilters: React.FC<ListingFiltersProps> = ({ filters, onFiltersChange }) => {
  const { register, handleSubmit, reset } = useForm({
    defaultValues: filters,
  });

  const onSubmit = (data: any) => {
    onFiltersChange(data);
  };

  const handleReset = () => {
    reset({
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
    onFiltersChange({
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
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
          <label className="label">Platform</label>
          <select {...register('platform')} className="input">
            <option value="">All Platforms</option>
            <option value="facebook">Facebook Marketplace</option>
            <option value="craigslist">Craigslist</option>
            <option value="mercadolibre">Mercado Libre</option>
          </select>
        </div>

        <div>
          <label className="label">Make</label>
          <input
            {...register('make')}
            type="text"
            placeholder="e.g., Toyota"
            className="input"
          />
        </div>

        <div>
          <label className="label">Model</label>
          <input
            {...register('model')}
            type="text"
            placeholder="e.g., Camry"
            className="input"
          />
        </div>

        <div>
          <label className="label">Condition</label>
          <select {...register('condition')} className="input">
            <option value="">All Conditions</option>
            <option value="new">New</option>
            <option value="used">Used</option>
            <option value="certified">Certified</option>
            <option value="salvage">Salvage</option>
          </select>
        </div>

        <div>
          <label className="label">Min Price</label>
          <input
            {...register('min_price')}
            type="number"
            placeholder="0"
            className="input"
          />
        </div>

        <div>
          <label className="label">Max Price</label>
          <input
            {...register('max_price')}
            type="number"
            placeholder="100000"
            className="input"
          />
        </div>

        <div>
          <label className="label">Min Year</label>
          <input
            {...register('min_year')}
            type="number"
            placeholder="2000"
            min="1900"
            max={new Date().getFullYear() + 1}
            className="input"
          />
        </div>

        <div>
          <label className="label">Max Year</label>
          <input
            {...register('max_year')}
            type="number"
            placeholder={new Date().getFullYear().toString()}
            min="1900"
            max={new Date().getFullYear() + 1}
            className="input"
          />
        </div>
      </div>

      <div className="flex justify-between items-center">
        <div>
          <label className="label">Days Back</label>
          <select {...register('days_back')} className="input w-32">
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
            <option value={365}>Last year</option>
          </select>
        </div>

        <div className="flex space-x-2">
          <button
            type="button"
            onClick={handleReset}
            className="btn btn-secondary"
          >
            Reset
          </button>
          <button type="submit" className="btn btn-primary">
            Apply Filters
          </button>
        </div>
      </div>
    </form>
  );
};

export default ListingFilters;
