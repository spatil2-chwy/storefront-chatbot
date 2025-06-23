import { Router } from 'express';
import { IStorage } from './storage';
import { userSchema, productSchema, chatMessageSchema } from '../shared/schema';
import { z } from 'zod';

export function createRoutes(storage: IStorage) {
  const router = Router();

  // Health check
  router.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
  });

  // Product routes
  router.get('/products', async (req, res) => {
    try {
      const { search, category } = req.query;
      
      let products;
      if (search) {
        products = await storage.searchProducts(search as string);
      } else if (category) {
        products = await storage.getProductsByCategory(category as string);
      } else {
        products = await storage.getAllProducts();
      }
      
      res.json(products);
    } catch (error) {
      console.error('Error fetching products:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  });

  router.get('/products/:id', async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      if (isNaN(id)) {
        return res.status(400).json({ error: 'Invalid product ID' });
      }

      const product = await storage.getProductById(id);
      if (!product) {
        return res.status(404).json({ error: 'Product not found' });
      }

      res.json(product);
    } catch (error) {
      console.error('Error fetching product:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  });

  // Authentication routes (mock implementation)
  const loginSchema = z.object({
    email: z.string().email(),
    password: z.string().min(1)
  });

  router.post('/auth/login', async (req, res) => {
    try {
      const { email, password } = loginSchema.parse(req.body);
      
      // Mock authentication - in real app, verify password hash
      let user = await storage.getUserByEmail(email);
      
      if (!user) {
        // Create mock user for demo
        user = await storage.createUser({
          email,
          name: email.split('@')[0]
        });
      }

      res.json({
        user,
        token: 'mock-jwt-token'
      });
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: 'Invalid request data', details: error.errors });
      }
      console.error('Login error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  });

  router.post('/auth/logout', (req, res) => {
    res.json({ message: 'Logged out successfully' });
  });

  router.get('/auth/me', async (req, res) => {
    // Mock current user - in real app, verify JWT token
    const mockUser = {
      id: 1,
      email: 'user@example.com',
      name: 'Test User'
    };
    res.json(mockUser);
  });

  // Chat routes
  const chatMessageInputSchema = z.object({
    content: z.string().min(1),
    sender: z.enum(['user', 'ai'])
  });

  router.post('/chat', async (req, res) => {
    try {
      const { content, sender } = chatMessageInputSchema.parse(req.body);
      
      // Save user message
      const userMessage = await storage.saveChatMessage({
        content,
        sender,
        timestamp: new Date()
      });

      // Generate AI response if user message
      let aiResponse;
      if (sender === 'user') {
        const responses = [
          "I'd be happy to help you find the perfect product for your pet!",
          "Based on your needs, I can recommend some great options.",
          "Let me help you find products that match what you're looking for.",
          "I can suggest some popular items that other customers love.",
          "What specific type of pet product are you looking for?"
        ];
        
        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        
        aiResponse = await storage.saveChatMessage({
          content: randomResponse,
          sender: 'ai',
          timestamp: new Date()
        });
      }

      res.json({
        userMessage,
        aiResponse: aiResponse || null
      });
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: 'Invalid request data', details: error.errors });
      }
      console.error('Chat error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  });

  router.get('/chat/history', async (req, res) => {
    try {
      const limit = parseInt(req.query.limit as string) || 50;
      const history = await storage.getChatHistory(limit);
      res.json(history);
    } catch (error) {
      console.error('Error fetching chat history:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  });

  return router;
}