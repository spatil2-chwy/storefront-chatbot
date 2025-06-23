import { User, Product, ChatMessage } from '../shared/schema';

export interface IStorage {
  // User operations
  getUserById(id: number): Promise<User | null>;
  getUserByEmail(email: string): Promise<User | null>;
  createUser(user: Omit<User, 'id'>): Promise<User>;
  
  // Product operations
  getAllProducts(): Promise<Product[]>;
  getProductById(id: number): Promise<Product | null>;
  searchProducts(query: string): Promise<Product[]>;
  getProductsByCategory(category: string): Promise<Product[]>;
  
  // Chat operations
  saveChatMessage(message: Omit<ChatMessage, 'id'>): Promise<ChatMessage>;
  getChatHistory(limit?: number): Promise<ChatMessage[]>;
}

export class MemStorage implements IStorage {
  private users: User[] = [];
  private products: Product[] = [];
  private chatMessages: ChatMessage[] = [];
  private nextUserId = 1;
  private nextProductId = 1;

  constructor() {
    // Initialize with mock data
    this.initializeMockData();
  }

  private initializeMockData() {
    // Add mock products
    this.products = [
      {
        id: 1,
        title: "Premium Dog Food - Adult Formula",
        brand: "Hill's Science Diet",
        price: 54.99,
        originalPrice: 64.99,
        autoshipPrice: 49.49,
        rating: 4.8,
        reviewCount: 1250,
        image: "/api/placeholder/300/300",
        images: ["/api/placeholder/300/300", "/api/placeholder/300/300"],
        deal: true,
        flavors: ["Chicken", "Beef", "Salmon"],
        sizes: [
          { name: "15 lb", price: 54.99, pricePerLb: "$3.67" },
          { name: "30 lb", price: 89.99, pricePerLb: "$3.00" }
        ],
        description: "Complete and balanced nutrition for adult dogs with high-quality protein and essential nutrients.",
        inStock: true,
        category: "Dog Food",
        keywords: ["premium", "nutrition", "adult", "dry food", "chicken", "protein"]
      },
      {
        id: 2,
        title: "Multi-Cat Clumping Litter",
        brand: "Fresh Step",
        price: 24.99,
        originalPrice: 29.99,
        autoshipPrice: 22.49,
        rating: 4.5,
        reviewCount: 890,
        image: "/api/placeholder/300/300",
        images: ["/api/placeholder/300/300"],
        deal: false,
        flavors: ["Unscented", "Fresh Scent"],
        sizes: [
          { name: "25 lb", price: 24.99, pricePerLb: "$1.00" }
        ],
        description: "Advanced odor control formula perfect for households with multiple cats.",
        inStock: true,
        category: "Cat Litter",
        keywords: ["odor control", "clumping", "multiple cats", "fresh", "unscented"]
      }
    ];

    this.nextProductId = this.products.length + 1;
  }

  // User operations
  async getUserById(id: number): Promise<User | null> {
    return this.users.find(user => user.id === id) || null;
  }

  async getUserByEmail(email: string): Promise<User | null> {
    return this.users.find(user => user.email === email) || null;
  }

  async createUser(userData: Omit<User, 'id'>): Promise<User> {
    const user: User = {
      ...userData,
      id: this.nextUserId++
    };
    this.users.push(user);
    return user;
  }

  // Product operations
  async getAllProducts(): Promise<Product[]> {
    return [...this.products];
  }

  async getProductById(id: number): Promise<Product | null> {
    return this.products.find(product => product.id === id) || null;
  }

  async searchProducts(query: string): Promise<Product[]> {
    const searchTerm = query.toLowerCase();
    return this.products.filter(product => 
      product.title.toLowerCase().includes(searchTerm) ||
      product.brand.toLowerCase().includes(searchTerm) ||
      product.category.toLowerCase().includes(searchTerm) ||
      product.keywords.some(keyword => keyword.toLowerCase().includes(searchTerm))
    );
  }

  async getProductsByCategory(category: string): Promise<Product[]> {
    return this.products.filter(product => 
      product.category.toLowerCase() === category.toLowerCase()
    );
  }

  // Chat operations
  async saveChatMessage(messageData: Omit<ChatMessage, 'id'>): Promise<ChatMessage> {
    const message: ChatMessage = {
      ...messageData,
      id: Date.now().toString()
    };
    this.chatMessages.push(message);
    return message;
  }

  async getChatHistory(limit: number = 50): Promise<ChatMessage[]> {
    return this.chatMessages
      .slice(-limit)
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
  }
}