import { useState, useEffect } from 'react';
import { Product } from '../../../types';
import { productsApi, ApiError } from '../../../lib/api';

// Generic hook for fetching any resource with loading and error states
export const useAsyncResource = <T>(
  fetchFn: () => Promise<T>,
  dependencies: any[] = []
) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await fetchFn();
        setData(result);
      } catch (err) {
        if (err instanceof ApiError) {
          setError(err.message);
        } else {
          setError('An unexpected error occurred');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, dependencies);

  return { data, loading, error };
};

// Specific hook for products using the generic hook
export const useProduct = (productId: number | null) => {
  const { data: product, loading, error } = useAsyncResource(
    () => productsApi.getProduct(productId!),
    [productId]
  );

  return { product, loading, error };
}; 