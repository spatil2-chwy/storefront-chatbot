import { useState, useEffect } from 'react';
import { Product } from '../types';
import { api, ApiError } from '../lib/api';

export const useProduct = (productId: number | null) => {
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!productId) {
      setProduct(null);
      setLoading(false);
      return;
    }

    const fetchProduct = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await api.getProduct(productId);
        setProduct(data);
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

    fetchProduct();
  }, [productId]);

  return { product, loading, error };
}; 