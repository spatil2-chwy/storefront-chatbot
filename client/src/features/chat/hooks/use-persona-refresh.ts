import { useCallback } from 'react';
import { useAuth } from '../../../lib/auth/auth-provider';

export const usePersonaRefresh = () => {
  const { refreshUser } = useAuth();

  const refreshPersonaAfterChat = useCallback(async (messageCount: number) => {
    // Refresh persona after every 4th message (matching server logic)
    if (messageCount > 0 && messageCount % 4 === 0) {
      try {
        console.log(`Refreshing persona after ${messageCount} messages`);
        await refreshUser();
      } catch (error) {
        console.error('Error refreshing persona after chat:', error);
      }
    }
  }, [refreshUser]);

  return { refreshPersonaAfterChat };
}; 