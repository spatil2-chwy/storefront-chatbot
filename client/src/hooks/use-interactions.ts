import { useCallback } from 'react';
import { interactionsApi, InteractionRequest } from '@/lib/api/interactions';
import { useAuth } from '@/lib/auth';
import { Product } from '@/types';

export const useInteractions = () => {
  const { user } = useAuth();

  const logInteraction = useCallback(async (
    eventType: 'purchase' | 'addToCart' | 'productClick',
    product?: Product,
    eventValue?: number
  ) => {
    if (!user?.customer_key) {
      console.warn('Cannot log interaction: no user logged in');
      return;
    }

    try {
      const interactionData: InteractionRequest = {
        customer_key: user.customer_key,
        event_type: eventType,
        item_id: product?.id,
        event_value: eventValue,
        product_metadata: product ? {
          title: product.title,
          brand: product.brand,
          price: product.price,
          category_level_1: product.category_level_1,
          category_level_2: product.category_level_2,
          keywords: product.keywords,
          rating: product.rating,
          reviewCount: product.reviewCount
        } : undefined
      };

      await interactionsApi.logInteraction(interactionData);
      console.log(`Interaction logged: ${eventType}`, interactionData);
    } catch (error) {
      console.error('Failed to log interaction:', error);
    }
  }, [user?.customer_key]);

  const logProductClick = useCallback((product: Product) => {
    return logInteraction('productClick', product);
  }, [logInteraction]);

  const logAddToCart = useCallback((product: Product, quantity: number = 1) => {
    const price = product.price || 0;
    return logInteraction('addToCart', product, price * quantity);
  }, [logInteraction]);

  const logPurchase = useCallback((product: Product, quantity: number = 1, purchaseOption: 'buyonce' | 'autoship' = 'buyonce') => {
    const price = purchaseOption === 'autoship' && product.autoshipPrice 
      ? product.autoshipPrice 
      : product.price || 0;
    return logInteraction('purchase', product, price * quantity);
  }, [logInteraction]);

  return {
    logInteraction,
    logProductClick,
    logAddToCart,
    logPurchase
  };
}; 